---
---
// Team member data from sitetext.yml via Liquid
const teamData = [
    {% for person in site.data.sitetext.en.team.people %}
    {
        name: "{{ person.name }}",
        role: "{{ person.role }}",
        email: "{{ person.email }}",
        phone: "{{ person.phone }}",
        image: "{{ person.image }}",
        linkedin: "{% for social in person.social %}{% if social.icon contains 'linkedin' %}{{ social.url }}{% endif %}{% endfor %}"
    }{% unless forloop.last %},{% endunless %}
    {% endfor %}
];

// Constants from sitetext.yml
const companyLinkedin = "{{ site.data.sitetext.en.footer.social[2].url }}";
const calendarUrl = "{{ site.data.sitetext.en.header.buttonlink }}";
const tagline = "{{ site.data.sitetext.en.services.text }}";

function loadTeamMember() {
    const select = document.getElementById('teamMember');
    const selectedValue = select.value;
    
    if (selectedValue && selectedValue !== 'custom' && teamData[selectedValue]) {
        const member = teamData[selectedValue];
        document.getElementById('fullName').value = member.name;
        document.getElementById('jobTitle').value = member.role;
        document.getElementById('email').value = member.email;
        document.getElementById('phone').value = member.phone;
        document.getElementById('profileImage').value = member.image;
        document.getElementById('linkedinUrl').value = member.linkedin;
    } else if (selectedValue === 'custom') {
        // Clear all fields for custom entry
        document.getElementById('fullName').value = '';
        document.getElementById('jobTitle').value = '';
        document.getElementById('email').value = '';
        document.getElementById('phone').value = '';
        document.getElementById('profileImage').value = '';
        document.getElementById('linkedinUrl').value = '';
    }
}

function generateSignature() {
    const fullName = document.getElementById('fullName').value;
    const jobTitle = document.getElementById('jobTitle').value;
    const email = document.getElementById('email').value;
    const phone = document.getElementById('phone').value;
    const profileImage = document.getElementById('profileImage').value;
    const linkedinUrl = document.getElementById('linkedinUrl').value;
    const bannerUrl = document.getElementById('bannerUrl').value;

    if (!fullName || !email) {
        alert('Please fill in at least the full name and email address.');
        return;
    }

    const htmlSignature = `<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Email Signature</title>
    <link href="https://fonts.googleapis.com/css?family=Atkinson+Hyperlegible:400,700&display=swap" rel="stylesheet">
</head>
<body>
    <table cellpadding="0" cellspacing="0" border="0" style="font-family: 'Atkinson Hyperlegible', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.2; color: #111d30;">
        <tr>
            <td style="vertical-align: top; padding-right: 15px;">
                ${profileImage ? `<img src="${profileImage}" alt="${fullName}" style="width: 80px; height: 80px; border-radius: 50%; object-fit: cover;${fullName === 'Nico Boyce' ? ' transform: scaleX(-1);' : ''};">` : ''}
            </td>
            <td style="vertical-align: top;">
                <table cellpadding="0" cellspacing="0" border="0">
                    <tr>
                        <td style="font-weight: bold; font-size: 14px; color: #111d30; padding-bottom: 2px;">
                            ${fullName}
                        </td>
                    </tr>
                    ${jobTitle ? `<tr><td style="font-weight: normal; font-size: 12px; color: #a04610; padding-bottom: 8px;">${jobTitle}, Deltastring</td></tr>` : ''}
                    <tr>
                        <td style="font-weight: bold; font-size: 11px; color: #111d30; padding-bottom: 2px;">
                            ${email}
                        </td>
                    </tr>
                    ${phone ? `<tr><td style="font-weight: bold; font-size: 11px; color: #111d30; padding-bottom: 8px;">${phone}</td></tr>` : ''}
                    
                    <tr>
                        <td style="padding-bottom: 8px;">
                            ${linkedinUrl ? `<a href="${linkedinUrl}" style="text-decoration: none; margin-right: 8px;"><img src="https://cdn-icons-png.flaticon.com/512/174/174857.png" alt="LinkedIn" style="width: 16px; height: 16px; vertical-align: middle;"></a>` : ''}
                            ${phone ? `<a href="https://wa.me/${phone.replace(/[^0-9]/g, '')}" style="text-decoration: none; margin-right: 8px;"><img src="https://cdn-icons-png.flaticon.com/512/733/733585.png" alt="WhatsApp" style="width: 16px; height: 16px; vertical-align: middle;"></a>` : ''}
                            <a href="${calendarUrl}" style="text-decoration: none; margin-right: 8px;">
                                <img src="https://cdn-icons-png.flaticon.com/512/3652/3652267.png" alt="Calendar" style="width: 16px; height: 16px; vertical-align: middle;">
                            </a>
                            <a href="https://deltastring.com" style="text-decoration: none;">
                                <img src="https://deltastring.com/assets/img/ds-icon-square.svg" alt="Deltastring" style="width: 16px; height: 16px; vertical-align: middle;">
                            </a>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
        
        <tr>
            <td colspan="2" style="padding-top: 8px; border-top: 1px solid #a04610;">
                <p style="font-size: 10px; color: #a04610; font-style: italic; margin: 4px 0 0 0;">
                    ${tagline}
                </p>
            </td>
        </tr>
    </table>
</body>
</html>`;

    // Display preview and HTML
    document.getElementById('signaturePreview').innerHTML = htmlSignature;
    document.getElementById('signatureHtml').textContent = htmlSignature;
    document.getElementById('output').classList.remove('hidden');
    document.getElementById('copyBtn').disabled = false;
    
    // Store for copying
    window.currentSignature = htmlSignature;
}

function copyToClipboard() {
    if (!window.currentSignature) {
        alert('Please generate a signature first.');
        return;
    }

    navigator.clipboard.writeText(window.currentSignature).then(function() {
        const alert = document.getElementById('copyAlert');
        alert.classList.remove('hidden');
        setTimeout(() => {
            alert.classList.add('hidden');
        }, 3000);
    }).catch(function(err) {
        console.error('Could not copy text: ', err);
        alert('Failed to copy to clipboard. Please manually select and copy the HTML code.');
    });
}