// Gradient Comparison Tool JavaScript

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
    console.log('updateAllGradients called');
    const color1 = document.getElementById('startColorText').value;
    const color2 = document.getElementById('endColorText').value;
    const weight = parseInt(document.getElementById('blendSlider').value) / 100;
    
    console.log('Colors:', color1, color2, 'Weight:', weight);
    
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
    
    const gradientStops = stops.join(', ');
    console.log('Setting gradient stops:', gradientStops);
    document.documentElement.style.setProperty('--gradient-stops', gradientStops);
    
    // Also try setting it directly on the element
    const blendedElement = document.getElementById('blendedGradient');
    if (blendedElement) {
        blendedElement.style.background = `linear-gradient(to right, ${gradientStops})`;
        console.log('Set background directly on blended element');
    } else {
        console.error('blendedGradient element not found!');
    }
}

// Initialize the tool when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, initializing gradient tool');
    
    // Event listeners
    document.getElementById('startColorPicker').addEventListener('input', (e) => {
        document.getElementById('startColorText').value = e.target.value;
        updateAllGradients();
    });
    
    document.getElementById('startColorText').addEventListener('input', (e) => {
        const value = e.target.value;
        if (/^#[0-9A-F]{6}$/i.test(value)) {
            document.getElementById('startColorPicker').value = value;
            updateAllGradients();
        }
    });
    
    document.getElementById('endColorPicker').addEventListener('input', (e) => {
        document.getElementById('endColorText').value = e.target.value;
        updateAllGradients();
    });
    
    document.getElementById('endColorText').addEventListener('input', (e) => {
        const value = e.target.value;
        if (/^#[0-9A-F]{6}$/i.test(value)) {
            document.getElementById('endColorPicker').value = value;
            updateAllGradients();
        }
    });
    
    document.getElementById('blendSlider').addEventListener('input', updateAllGradients);
    
    // Initial render
    updateAllGradients();
});

// Fallback in case DOMContentLoaded already fired
if (document.readyState === 'loading') {
    console.log('DOM still loading, waiting for DOMContentLoaded');
} else {
    console.log('DOM already ready, running gradient tool initialization immediately');
    // Run the same initialization code
    if (typeof updateAllGradients !== 'undefined') {
        updateAllGradients();
    }
}