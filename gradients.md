---
layout: page
title: "Gradient Comparison Tool"
permalink: /gradients/
---

<style>
    .gradient-container {
        margin-bottom: 40px;
    }
    
    .gradient-bar {
        width: 100%;
        height: 100px;
        margin-bottom: 10px;
        border-radius: 8px;
    }
    
    .rgb-gradient {
        background: linear-gradient(to right, #eb7824, #111d30);
    }
    
    .oklch-gradient {
        background: linear-gradient(to right in oklch, #eb7824, #111d30);
    }
    
    .colours {
        font-family: monospace;
        font-size: 14px;
        opacity: 0.8;
        margin-bottom: 10px;
    }
    
    .note {
        font-size: 12px;
        opacity: 0.6;
        margin-top: 20px;
    }
    
    .blended-gradient {
        background: linear-gradient(to right, var(--gradient-stops));
    }
    
    .controls {
        margin: 20px 0;
    }
    
    .main-controls {
        margin: 20px 0;
        padding: 20px;
        background: #333;
        border-radius: 8px;
        color: white;
    }
    
    .colour-inputs {
        display: flex;
        gap: 20px;
        align-items: center;
        margin-bottom: 20px;
    }
    
    .colour-input {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 5px;
    }
    
    .colour-input label {
        color: white;
    }
    
    input[type="color"] {
        width: 60px;
        height: 40px;
        border: none;
        border-radius: 4px;
        cursor: pointer;
    }
    
    input[type="text"] {
        width: 80px;
        padding: 5px;
        border: 1px solid #555;
        background: #222;
        color: white;
        border-radius: 4px;
        text-align: center;
        font-family: monospace;
    }
    
    input[type="range"] {
        width: 200px;
        margin: 0 10px;
    }
    
    .controls label {
        color: white;
    }
    
    #blendValue {
        color: white;
    }
</style>

<div class="main-controls">
    <div class="colour-inputs">
        <div class="colour-input">
            <label>Start Colour</label>
            <input type="color" id="startColorPicker" value="#eb7824">
            <input type="text" id="startColorText" value="#eb7824">
        </div>
        <div class="colour-input">
            <label>End Colour</label>
            <input type="color" id="endColorPicker" value="#111d30">
            <input type="text" id="endColorText" value="#111d30">
        </div>
    </div>
    
    <div class="controls">
        <label>RGB ← → OKLCH</label>
        <input type="range" id="blendSlider" min="0" max="100" value="50">
        <span id="blendValue">50%</span>
    </div>
</div>

<div class="gradient-container">
    <h2>RGB Linear Gradient</h2>
    <div class="colours" id="rgbColours">#eb7824 (orange) → #111d30 (dark blue)</div>
    <div class="gradient-bar rgb-gradient" id="rgbGradient"></div>
</div>

<div class="gradient-container">
    <h2>OKLCH Gradient</h2>
    <div class="colours" id="oklchColours">#eb7824 (orange) → #111d30 (dark blue)</div>
    <div class="gradient-bar oklch-gradient" id="oklchGradient"></div>
</div>

<div class="gradient-container">
    <h2>Blended Gradient</h2>
    <div class="colours" id="blendedColours">#eb7824 (orange) → #111d30 (dark blue)</div>
    <div class="gradient-bar blended-gradient" id="blendedGradient"></div>
</div>

<div class="note">
    Note: The RGB gradient interpolates linearly through RGB space (straight line).
    The OKLCH gradient interpolates through perceptual colour space, taking the shorter arc around the hue wheel.
    The blended gradient averages both approaches at each point.
    OKLCH may not be supported in all browsers.
</div>

<script>
    // Simple RGB interpolation
    function hexToRgb(hex) {
        const r = parseInt(hex.slice(1, 3), 16);
        const g = parseInt(hex.slice(3, 5), 16);
        const b = parseInt(hex.slice(5, 7), 16);
        return { r, g, b };
    }
    
    function rgbToHex(r, g, b) {
        return "#" + [r, g, b].map(x => Math.round(x).toString(16).padStart(2, '0')).join('');
    }
    
    function interpolateRgb(color1, color2, t) {
        const c1 = hexToRgb(color1);
        const c2 = hexToRgb(color2);
        
        return {
            r: c1.r + (c2.r - c1.r) * t,
            g: c1.g + (c2.g - c1.g) * t,
            b: c1.b + (c2.b - c1.b) * t
        };
    }
    
    // Basic OKLCH approximation (simplified)
    function rgbToOklch(r, g, b) {
        // Simplified conversion - real OKLCH needs proper colour space math
        const max = Math.max(r, g, b) / 255;
        const min = Math.min(r, g, b) / 255;
        const l = (max + min) / 2;
        
        let h = 0;
        if (max !== min) {
            if (r / 255 === max) h = ((g - b) / 255) / (max - min);
            else if (g / 255 === max) h = 2 + ((b - r) / 255) / (max - min);
            else h = 4 + ((r - g) / 255) / (max - min);
            h *= 60;
            if (h < 0) h += 360;
        }
        
        const c = max - min;
        return { l, c, h };
    }
    
    function oklchToRgb(l, c, h) {
        // Simplified back-conversion
        const hRad = (h * Math.PI) / 180;
        const a = c * Math.cos(hRad);
        const b = c * Math.sin(hRad);
        
        // Simplified RGB approximation
        let r = l + 0.4 * a;
        let g = l - 0.2 * a + 0.6 * b;
        let blue = l - 0.4 * a - 0.2 * b;
        
        return {
            r: Math.max(0, Math.min(255, r * 255)),
            g: Math.max(0, Math.min(255, g * 255)),
            b: Math.max(0, Math.min(255, blue * 255))
        };
    }
    
    function interpolateOklch(color1, color2, t) {
        const c1 = hexToRgb(color1);
        const c2 = hexToRgb(color2);
        
        const oklch1 = rgbToOklch(c1.r, c1.g, c1.b);
        const oklch2 = rgbToOklch(c2.r, c2.g, c2.b);
        
        // Interpolate hue taking shorter path
        let hDiff = oklch2.h - oklch1.h;
        if (hDiff > 180) hDiff -= 360;
        if (hDiff < -180) hDiff += 360;
        
        const interpL = oklch1.l + (oklch2.l - oklch1.l) * t;
        const interpC = oklch1.c + (oklch2.c - oklch1.c) * t;
        const interpH = oklch1.h + hDiff * t;
        
        return oklchToRgb(interpL, interpC, interpH);
    }
    
    function updateAllGradients() {
        const color1 = document.getElementById('startColorText').value;
        const color2 = document.getElementById('endColorText').value;
        const weight = parseInt(document.getElementById('blendSlider').value) / 100;
        
        // Update blend value display
        document.getElementById('blendValue').textContent = Math.round(weight * 100) + '%';
        
        // Update colour labels
        const colourText = `${color1} → ${color2}`;
        document.getElementById('rgbColours').textContent = colourText;
        document.getElementById('oklchColours').textContent = colourText;
        document.getElementById('blendedColours').textContent = colourText;
        
        // Update RGB gradient
        document.getElementById('rgbGradient').style.background = 
            `linear-gradient(to right, ${color1}, ${color2})`;
        
        // Update OKLCH gradient
        document.getElementById('oklchGradient').style.background = 
            `linear-gradient(to right in oklch, ${color1}, ${color2})`;
        
        // Update blended gradient
        const steps = 20;
        const stops = [];
        
        for (let i = 0; i <= steps; i++) {
            const t = i / steps;
            
            let blended;
            
            // Force exact endpoints to match original colours
            if (t === 0) {
                blended = hexToRgb(color1);
            } else if (t === 1) {
                blended = hexToRgb(color2);
            } else {
                const rgbColor = interpolateRgb(color1, color2, t);
                const oklchColor = interpolateOklch(color1, color2, t);
                
                // Blend the two approaches
                blended = {
                    r: rgbColor.r * (1 - weight) + oklchColor.r * weight,
                    g: rgbColor.g * (1 - weight) + oklchColor.g * weight,
                    b: rgbColor.b * (1 - weight) + oklchColor.b * weight
                };
            }
            
            const hex = rgbToHex(blended.r, blended.g, blended.b);
            const percent = (t * 100).toFixed(0);
            stops.push(`${hex} ${percent}%`);
        }
        
        document.documentElement.style.setProperty('--gradient-stops', stops.join(', '));
    }
    
    function syncColourInputs(sourceId, targetPickerId, targetTextId) {
        const value = document.getElementById(sourceId).value;
        document.getElementById(targetPickerId).value = value;
        document.getElementById(targetTextId).value = value;
        updateAllGradients();
    }
    
    // Event listeners
    document.getElementById('startColorPicker').addEventListener('input', () => 
        syncColourInputs('startColorPicker', 'startColorPicker', 'startColorText'));
    
    document.getElementById('startColorText').addEventListener('input', () => {
        const value = document.getElementById('startColorText').value;
        if (/^#[0-9A-F]{6}$/i.test(value)) {
            document.getElementById('startColorPicker').value = value;
            updateAllGradients();
        }
    });
    
    document.getElementById('endColorPicker').addEventListener('input', () => 
        syncColourInputs('endColorPicker', 'endColorPicker', 'endColorText'));
    
    document.getElementById('endColorText').addEventListener('input', () => {
        const value = document.getElementById('endColorText').value;
        if (/^#[0-9A-F]{6}$/i.test(value)) {
            document.getElementById('endColorPicker').value = value;
            updateAllGradients();
        }
    });
    
    document.getElementById('blendSlider').addEventListener('input', updateAllGradients);
    
    // Wait for page load
    document.addEventListener('DOMContentLoaded', updateAllGradients);
</script>