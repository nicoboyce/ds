document.addEventListener('DOMContentLoaded', function() {
    const copyButtons = document.querySelectorAll('.copy-signature');
    console.log('Found ' + copyButtons.length + ' copy buttons');
    
    copyButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const personSlug = this.getAttribute('data-person');
            console.log('Copying signature for:', personSlug);
            
            const signatureElement = document.getElementById('signature-' + personSlug);
            
            if (!signatureElement) {
                console.error('Signature element not found for:', personSlug);
                alert('Error: Could not find signature element');
                return;
            }
            
            // Select the signature element content
            const range = document.createRange();
            range.selectNodeContents(signatureElement);
            const selection = window.getSelection();
            selection.removeAllRanges();
            selection.addRange(range);
            
            let successful = false;
            try {
                // Copy the selection - this copies the rendered HTML, not the source
                successful = document.execCommand('copy');
                console.log('Copy command result:', successful);
            } catch (err) {
                console.error('Copy command failed:', err);
            }
            
            // Clear selection after copying
            selection.removeAllRanges();
            
            if (successful) {
                // Update button text temporarily
                const originalText = this.innerHTML;
                this.innerHTML = '<i class="fa fa-check"></i> Copied!';
                this.classList.remove('btn-primary');
                this.classList.add('btn-success');
                
                setTimeout(() => {
                    this.innerHTML = originalText;
                    this.classList.remove('btn-success');
                    this.classList.add('btn-primary');
                }, 2000);
            } else {
                // Fallback: re-select for manual copying
                const range = document.createRange();
                range.selectNodeContents(signatureElement);
                const selection = window.getSelection();
                selection.removeAllRanges();
                selection.addRange(range);
                
                alert('Auto-copy failed. The signature has been selected - please press Ctrl+C (Cmd+C on Mac) to copy');
            }
        });
    });
});