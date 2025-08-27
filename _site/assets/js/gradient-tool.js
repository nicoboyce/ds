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

// Proper OKLCH colour space conversion
function multiplyMatrix(matrix, vector) {
    return [
        matrix[0][0] * vector[0] + matrix[0][1] * vector[1] + matrix[0][2] * vector[2],
        matrix[1][0] * vector[0] + matrix[1][1] * vector[1] + matrix[1][2] * vector[2],
        matrix[2][0] * vector[0] + matrix[2][1] * vector[1] + matrix[2][2] * vector[2]
    ];
}

function rgbToLinear(c) {
    return c <= 0.04045 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
}

function linearToRgb(c) {
    return c <= 0.0031308 ? c * 12.92 : 1.055 * Math.pow(c, 1 / 2.4) - 0.055;
}

function rgbToOklch(r, g, b) {
    // Normalise RGB to 0-1
    r /= 255;
    g /= 255;
    b /= 255;
    
    // Convert to linear RGB
    const lr = rgbToLinear(r);
    const lg = rgbToLinear(g);
    const lb = rgbToLinear(b);
    
    // Convert linear RGB to XYZ (sRGB matrix)
    const xyz = multiplyMatrix([
        [0.4124564, 0.3575761, 0.1804375],
        [0.2126729, 0.7151522, 0.0721750],
        [0.0193339, 0.1191920, 0.9503041]
    ], [lr, lg, lb]);
    
    // Convert XYZ to Oklab
    const lms = multiplyMatrix([
        [0.8189330101, 0.3618667424, -0.1288597137],
        [0.0329845436, 0.9293118715, 0.0361456387],
        [0.0482003018, 0.2643662691, 0.6338517070]
    ], xyz);
    
    // Apply cube root
    const lmsRoot = lms.map(c => Math.sign(c) * Math.pow(Math.abs(c), 1/3));
    
    // Convert to Oklab
    const lab = multiplyMatrix([
        [0.2104542553, 0.7936177850, -0.0040720468],
        [1.9779984951, -2.4285922050, 0.4505937099],
        [0.0259040371, 0.7827717662, -0.8086757660]
    ], lmsRoot);
    
    // Convert Lab to LCH
    const l = lab[0];
    const a = lab[1];
    const bComp = lab[2];
    
    const c = Math.sqrt(a * a + bComp * bComp);
    let h = Math.atan2(bComp, a) * 180 / Math.PI;
    if (h < 0) h += 360;
    
    return { l, c, h };
}

function oklchToRgb(l, c, h) {
    // Convert LCH to Lab
    const hRad = h * Math.PI / 180;
    const a = c * Math.cos(hRad);
    const bComp = c * Math.sin(hRad);
    
    // Convert Oklab to LMS
    const lmsRoot = multiplyMatrix([
        [1, 0.3963377774, 0.2158037573],
        [1, -0.1055613458, -0.0638541728],
        [1, -0.0894841775, -1.2914855480]
    ], [l, a, bComp]);
    
    // Apply cube
    const lms = lmsRoot.map(c => c * c * c);
    
    // Convert LMS to XYZ
    const xyz = multiplyMatrix([
        [1.2268798733, -0.5578149965, 0.2813910456],
        [-0.0405801784, 1.1122568696, -0.0716766787],
        [-0.0763812845, -0.4214819784, 1.5861632204]
    ], lms);
    
    // Convert XYZ to linear RGB
    const linearRgb = multiplyMatrix([
        [3.2404542, -1.5371385, -0.4985314],
        [-0.9692660, 1.8760108, 0.0415560],
        [0.0556434, -0.2040259, 1.0572252]
    ], xyz);
    
    // Convert linear RGB to sRGB
    const rgb = linearRgb.map(c => linearToRgb(Math.max(0, Math.min(1, c))));
    
    return {
        r: Math.round(rgb[0] * 255),
        g: Math.round(rgb[1] * 255),
        b: Math.round(rgb[2] * 255)
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
        
        if (weight === 0) {
            // Pure RGB interpolation
            blended = interpolateRgb(color1, color2, t);
        } else if (weight === 1) {
            // Pure OKLCH interpolation
            blended = interpolateOklch(color1, color2, t);
        } else {
            // Weighted blend between RGB and OKLCH
            const rgbColor = interpolateRgb(color1, color2, t);
            const oklchColor = interpolateOklch(color1, color2, t);
            
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