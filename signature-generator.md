---
layout: default
title: Email Signature Generator
sitemap: false
---

<style>
body {
    font-family: 'Lato', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background-color: #eff0e9;
}
.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
    background: white;
    border-radius: 10px;
    box-shadow: 0 2px 10px rgba(17,29,48,0.1);
}
h1 {
    color: #111d30;
    font-family: 'Atkinson Hyperlegible', sans-serif;
    text-align: center;
    margin-bottom: 30px;
}
.form-section {
    margin-bottom: 30px;
    padding: 20px;
    background: #eff0e9;
    border-radius: 8px;
    border: 1px solid #a04610;
}
.form-group {
    margin-bottom: 15px;
}
label {
    display: block;
    margin-bottom: 5px;
    font-weight: 600;
    color: #111d30;
}
select, input[type="text"], input[type="email"], input[type="tel"] {
    width: 100%;
    padding: 10px;
    border: 2px solid #a04610;
    border-radius: 5px;
    font-size: 14px;
    font-family: 'Lato', sans-serif;
}
select:focus, input[type="text"]:focus, input[type="email"]:focus, input[type="tel"]:focus {
    outline: none;
    border-color: #111d30;
}
.button-group {
    display: flex;
    gap: 10px;
    margin-top: 20px;
}
button {
    padding: 12px 24px;
    border: none;
    border-radius: 5px;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    transition: background-color 0.2s;
}
.btn-primary {
    background-color: #a04610;
    color: #eff0e9;
}
.btn-primary:hover {
    background-color: #111d30;
}
.btn-success {
    background-color: #111d30;
    color: #eff0e9;
}
.btn-success:hover {
    background-color: #a04610;
}
.output-section {
    margin-top: 30px;
    padding: 20px;
    background: #fff;
    border: 2px solid #a04610;
    border-radius: 8px;
}
.signature-preview {
    border: 2px solid #a04610;
    padding: 20px;
    margin: 15px 0;
    border-radius: 5px;
    background: white;
}
.signature-html {
    font-family: monospace;
    font-size: 12px;
    background: #eff0e9;
    padding: 15px;
    border-radius: 5px;
    border: 1px solid #a04610;
    white-space: pre-wrap;
    word-wrap: break-word;
    max-height: 400px;
    overflow-y: auto;
}
.instructions {
    background: #eff0e9;
    padding: 20px;
    border-radius: 8px;
    margin-top: 20px;
    border-left: 4px solid #a04610;
}
.instructions h3 {
    margin-top: 0;
    color: #111d30;
    font-family: 'Atkinson Hyperlegible', sans-serif;
}
.alert {
    padding: 12px;
    border-radius: 5px;
    margin: 10px 0;
}
.alert-success {
    background-color: #eff0e9;
    border: 1px solid #a04610;
    color: #111d30;
}
.hidden {
    display: none;
}
.two-column {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
}
@media (max-width: 768px) {
    .two-column {
        grid-template-columns: 1fr;
    }
}
</style>

<div class="container">
    <h1>📧 Deltastring Email Signature Generator</h1>
    
    <div class="form-section">
        <div class="form-group">
            <label for="teamMember">Select Team Member:</label>
            <select id="teamMember" onchange="loadTeamMember()">
                <option value="">-- Select a team member --</option>
                <option value="custom">-- Custom (new team member) --</option>
                {% for person in site.data.sitetext.en.team.people %}
                <option value="{{ forloop.index0 }}">{{ person.name }}</option>
                {% endfor %}
            </select>
        </div>

        <div class="two-column">
            <div>
                <div class="form-group">
                    <label for="fullName">Full Name:</label>
                    <input type="text" id="fullName" placeholder="Enter full name">
                </div>
                
                <div class="form-group">
                    <label for="jobTitle">Job Title:</label>
                    <input type="text" id="jobTitle" placeholder="e.g. Senior Developer">
                </div>
                
                <div class="form-group">
                    <label for="email">Email Address:</label>
                    <input type="email" id="email" placeholder="name@deltastring.com">
                </div>
                
                <div class="form-group">
                    <label for="phone">Phone Number:</label>
                    <input type="tel" id="phone" placeholder="+44-XXXX-XXXXXX">
                </div>
            </div>
            
            <div>
                <div class="form-group">
                    <label for="profileImage">Profile Image URL:</label>
                    <input type="text" id="profileImage" placeholder="https://deltastring.com/assets/img/team/...">
                </div>
                
                <div class="form-group">
                    <label for="linkedinUrl">Personal LinkedIn URL:</label>
                    <input type="text" id="linkedinUrl" placeholder="https://linkedin.com/in/...">
                </div>
                
                <div class="form-group">
                    <label for="bannerUrl">Banner Image URL:</label>
                    <input type="text" id="bannerUrl" value="https://deltastring.com/assets/img/email-banner.png" placeholder="https://deltastring.com/assets/img/email-banner.png">
                </div>
            </div>
        </div>
        
        <div class="button-group">
            <button type="button" class="btn-primary" onclick="generateSignature()">Generate Signature</button>
            <button type="button" class="btn-success" onclick="copyToClipboard()" id="copyBtn" disabled>📋 Copy HTML to Clipboard</button>
        </div>
    </div>

    <div id="output" class="output-section hidden">
        <h3>📧 Signature Preview:</h3>
        <div id="signaturePreview" class="signature-preview"></div>
        
        <h3>📝 HTML Code:</h3>
        <div id="signatureHtml" class="signature-html"></div>
        
        <div id="copyAlert" class="alert alert-success hidden">
            ✅ Signature copied to clipboard!
        </div>
    </div>

    <div class="instructions">
        <h3>📱 How to Add This Signature to Gmail (Additional Account):</h3>
        <ol>
            <li><strong>Access Gmail Settings:</strong>
                <ul>
                    <li>Open Gmail in your browser</li>
                    <li>Click the gear icon (⚙️) in the top right</li>
                    <li>Select "Settings" from the dropdown</li>
                </ul>
            </li>
            <li><strong>Navigate to Accounts:</strong>
                <ul>
                    <li>Click on the "Accounts and Import" tab</li>
                    <li>Find the "Send mail as:" section</li>
                    <li>Locate your additional Deltastring email account</li>
                </ul>
            </li>
            <li><strong>Edit Account Settings:</strong>
                <ul>
                    <li>Click "Edit info" next to your Deltastring email</li>
                    <li>In the popup, you'll see signature options</li>
                </ul>
            </li>
            <li><strong>Add Your Signature:</strong>
                <ul>
                    <li>Click the "Copy HTML to Clipboard" button above</li>
                    <li>In Gmail, paste (Ctrl+V or Cmd+V) into the signature box</li>
                    <li>The formatting should appear automatically</li>
                    <li>Click "Save Changes"</li>
                </ul>
            </li>
            <li><strong>Set as Default:</strong>
                <ul>
                    <li>Back in main Settings, go to "General" tab</li>
                    <li>In the "Signature" section, select your Deltastring account</li>
                    <li>Choose the signature you just created</li>
                    <li>Save settings</li>
                </ul>
            </li>
        </ol>
        
        <p><strong>💡 Pro Tips:</strong></p>
        <ul>
            <li>Test by composing a new email from your Deltastring account</li>
            <li>The signature should appear automatically in new emails</li>
            <li>You can have different signatures for different email accounts</li>
            <li>If images don't load, check that the URLs are accessible publicly</li>
        </ul>
    </div>
</div>

<script src="/assets/js/signature-generator.js"></script>