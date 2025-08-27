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
        background: linear-gradient(to right, var(--gradient-stops, #eb7824 0%, #111d30 100%));
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
            <label for="startColorPicker">Start Colour</label>
            <input type="color" id="startColorPicker" value="#eb7824">
            <input type="text" id="startColorText" value="#eb7824" aria-label="Start colour hex code">
        </div>
        <div class="colour-input">
            <label for="endColorPicker">End Colour</label>
            <input type="color" id="endColorPicker" value="#111d30">
            <input type="text" id="endColorText" value="#111d30" aria-label="End colour hex code">
        </div>
    </div>
    
    <div class="controls">
        <label for="blendSlider">RGB ← → OKLCH</label>
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

<script src="/assets/js/gradient-tool.js"></script>