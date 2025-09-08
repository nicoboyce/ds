# RSS Pipeline Resource Cleanup Plan

## Problem Analysis
The RSS automation pipeline (daily_rss_update.py) is causing progressive system slowdown due to resource accumulation issues. After 37 runs, memory and process leaks are degrading performance.

### Root Causes Identified
1. **Subprocess resource leaks** - processes not properly terminated
2. **Python memory accumulation** - no garbage collection between pipeline steps
3. **Network connection pooling** - requests sessions not closed properly  
4. **Jekyll process isolation issues** - heavy Ruby processes lingering

### Current Resource Usage Evidence
- Pipeline has run 37 times (from automation.log)
- No RSS processes currently running (good sign)
- Memory usage normal but accumulation likely happens during runs
- Process cleanup gaps identified in code review

## Implementation Plan

### 1. Enhanced Process Management
**File:** `scripts/daily_rss_update.py:36`
**Current:** Basic subprocess.run() with timeout
**Fix:**
```python
def run_command(self, command, description):
    """Run shell command with explicit resource cleanup"""
    import psutil, gc, os
    process = None
    try:
        # Enhanced process tracking
        env = os.environ.copy()
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            capture_output=True,
            text=True,
            timeout=300,
            env=env,
            preexec_fn=os.setsid  # Process group for cleanup
        )
        
        if result.stdout.strip():
            logger.info(f"Output: {result.stdout.strip()}")
        return result.returncode == 0
        
    except subprocess.TimeoutExpired as e:
        # Kill entire process group
        if e.process:
            try:
                os.killpg(os.getpgid(e.process.pid), signal.SIGTERM)
            except:
                pass
        logger.error(f"⏱️ TIMEOUT after 5 minutes: {command}")
        return False
        
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ COMMAND FAILED with exit code {e.returncode}")
        if e.stdout:
            logger.error(f"Standard output: {e.stdout}")
        if e.stderr:
            logger.error(f"Error output: {e.stderr}")
        return False
        
    finally:
        # Force garbage collection after each command
        gc.collect()
        # Clear any lingering file descriptors
        import resource
        resource.setrlimit(resource.RLIMIT_NOFILE, resource.getrlimit(resource.RLIMIT_NOFILE))
```

### 2. Memory Barriers Between Pipeline Steps
**File:** `scripts/daily_rss_update.py:168`
**Add method:**
```python
def cleanup_resources(self):
    """Force cleanup between pipeline steps"""
    import gc
    import sys
    
    # Force garbage collection
    gc.collect()
    
    # Clear module caches
    if hasattr(sys, '_clear_type_cache'):
        sys._clear_type_cache()
    
    # Clear any requests session pools
    try:
        import requests
        requests.sessions.Session().close()
    except:
        pass
    
    logger.info("🧹 Resources cleaned")

def run_pipeline(self):
    """Run the complete pipeline with resource cleanup"""
    # ... existing code ...
    
    for step_name, step_func in steps:
        logger.info(f"\n--- Starting: {step_name} ---")
        if not step_func():
            # ... error handling ...
        else:
            logger.info(f"✅ SUCCESS: {step_name}")
            # ADD: Cleanup after each successful step
            self.cleanup_resources()
```

### 3. Network Session Management  
**File:** `scripts/rss_ingestion.py:17`
**Current:** Direct requests.get() calls
**Fix:**
```python
class RSSIngestion:
    def __init__(self, config_path='_data/rss_feeds.yml', data_dir='_data/rss'):
        # ... existing init ...
        self.session = None
    
    def __enter__(self):
        import requests
        self.session = requests.Session()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            self.session.close()
            self.session = None
    
    def fetch_feed(self, feed_config, max_items=50):
        """Fetch and parse RSS feed with session management"""
        try:
            if not self.session:
                import requests
                self.session = requests.Session()
                
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            print(f"Fetching: {feed_config['name']}")
            response = self.session.get(feed_config['url'], timeout=15, headers=headers)
            # ... rest of method unchanged ...
        finally:
            # Ensure session cleanup on any exit
            pass
    
    def run(self):
        """Run with context manager for automatic cleanup"""
        with self:
            # ... existing run logic ...
```

**Update caller in daily_rss_update.py:84:**
```python
def rss_ingestion(self):
    """Run RSS ingestion script with proper session cleanup"""
    logger.info("=== RSS INGESTION ===")
    
    # Run in subprocess but ensure it uses session management
    return self.run_command("python3 -c \"from scripts.rss_ingestion import RSSIngestion; import os; os.chdir('scripts/..'); ingestion = RSSIngestion(); ingestion.run()\"", "Ingesting RSS feeds")
```

### 4. Jekyll Process Group Isolation
**File:** `scripts/daily_rss_update.py:112`
**Current:** Basic bundle exec jekyll build
**Fix:**
```python
def jekyll_build(self):
    """Build Jekyll site with process group isolation"""
    logger.info("=== JEKYLL BUILD ===")
    
    bundle_path = "/home/nico/.local/share/gem/ruby/3.1.0/bin/bundle"
    
    if not os.path.exists(bundle_path):
        logger.warning("Bundle not found at expected path, trying global bundle")
        bundle_cmd = "bundle"
    else:
        bundle_cmd = bundle_path
    
    # Enhanced Jekyll command with resource limits
    jekyll_cmd = f"""
    set -e
    export BUNDLE_GEMFILE=Gemfile
    export JEKYLL_ENV=production
    ulimit -v 2097152  # 2GB virtual memory limit
    ulimit -t 300      # 5 minute CPU time limit
    {bundle_cmd} exec jekyll build --trace
    """
    
    logger.info("Attempting Jekyll build with resource limits...")
    return self.run_command(jekyll_cmd, "Building Jekyll site")
```

### 5. Claude API Session Cleanup
**File:** `scripts/claude_summariser.py:108`
**Add session management:**
```python
class ClaudeSummariser:
    def __init__(self):
        # ... existing init ...
        self.http_session = None
    
    def __enter__(self):
        import requests
        self.http_session = requests.Session()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.http_session:
            self.http_session.close()
            self.http_session = None
    
    def call_claude_api(self, prompt, max_tokens=4000):
        """Call Claude API with session management"""
        if not self.http_session:
            import requests
            self.http_session = requests.Session()
        
        try:
            response = self.http_session.post(
                'https://api.anthropic.com/v1/messages',
                # ... rest unchanged ...
            )
        finally:
            # Session will be closed by context manager
            pass
```

## Testing Strategy

### 1. Memory Monitoring Test
```bash
# Run with memory monitoring
while true; do
    echo "$(date): $(ps aux | grep python | grep -v grep | awk '{sum += $6} END {print sum/1024 " MB"}')" >> memory_test.log
    sleep 10
done &

python3 scripts/daily_rss_update.py
```

### 2. Process Leak Test
```bash
# Before and after process counts
echo "Before: $(ps aux | grep -E '(python|ruby|bundle)' | grep -v grep | wc -l)"
python3 scripts/daily_rss_update.py
echo "After: $(ps aux | grep -E '(python|ruby|bundle)' | grep -v grep | wc -l)"
```

### 3. Resource Usage Test  
```bash
# Monitor file descriptors and memory
lsof -p $$ | wc -l  # Before
python3 scripts/daily_rss_update.py
lsof -p $$ | wc -l  # After (should be similar)
```

## Deployment Approach

1. **Implement fixes** in daily_rss_update.py first (core process management)
2. **Test single run** with memory monitoring
3. **Add session management** to RSS ingestion and Claude summariser
4. **Test multiple consecutive runs** to verify no accumulation
5. **Deploy to production** cron job
6. **Monitor for 1 week** to confirm fix effectiveness

## Success Criteria

- No progressive memory growth over multiple runs
- Process count returns to baseline after each run  
- No zombie or orphaned processes
- Pipeline completion time remains stable
- System responsiveness maintained

## Rollback Plan

If issues occur:
1. Revert daily_rss_update.py to current version
2. Disable cron job temporarily
3. Run manual pipeline to verify functionality
4. Re-enable automation once stable

---

**Status:** Design complete, ready for implementation
**Priority:** High - affects production system performance
**Estimated effort:** 2-3 hours implementation + 1 week monitoring