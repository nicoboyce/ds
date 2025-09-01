# Email Signature Setup Instructions

## Files Created

### Templates (for future team members):
- `email-signature-template.html` - HTML template with variables
- `email-signature-template.txt` - Plain text template with variables

### Ready-to-use signatures:
- `nico-boyce-signature.html` / `nico-boyce-signature.txt`
- `rosie-elliott-welch-signature.html` / `rosie-elliott-welch-signature.txt`

## Banner Setup

### Current Banner URL
The signatures reference: `https://deltastring.com/assets/img/email-banner.png`

### Creating the Banner
1. Create an email banner image (recommended: 600px wide, 150-200px high)
2. Consider using the Deltastring logo from `assets/img/ds-logo-trans.svg` 
3. Save as `email-banner.png` in your `assets/img/` directory
4. Upload to your website at `/assets/img/email-banner.png`

### Banner Benefits
- **Centrally managed**: Update the banner file on your website to update all signatures
- **Consistent branding**: All team members use the same banner
- **Easy updates**: No need to redistribute signatures for banner changes

## Template Variables

When creating signatures for new team members, replace these variables:

### HTML Template Variables:
- `{{BANNER_URL}}` - Banner image URL
- `{{PROFILE_IMAGE}}` - Team member's profile photo URL  
- `{{FULL_NAME}}` - Full name
- `{{JOB_TITLE}}` - Job title
- `{{EMAIL}}` - Email address
- `{{PHONE}}` - Phone number
- `{{PERSONAL_LINKEDIN}}` - Personal LinkedIn profile URL

### Text Template Variables:
- `{{FULL_NAME}}` - Full name
- `{{JOB_TITLE}}` - Job title  
- `{{EMAIL}}` - Email address
- `{{PHONE}}` - Phone number
- `{{PERSONAL_LINKEDIN}}` - Personal LinkedIn profile URL

## Email Client Setup

### Outlook
1. Go to File > Options > Mail > Signatures
2. Click "New" and paste HTML signature
3. Set as default for new emails and replies

### Gmail
1. Go to Settings > General > Signature
2. Paste HTML signature in the rich text editor
3. Save changes

### Apple Mail
1. Go to Mail > Preferences > Signatures
2. Create new signature and paste HTML
3. Ensure "Always match my default message font" is unchecked

## Notes
- HTML signatures include profile images, social links, and formatting
- Plain text versions provided as fallback for older email clients
- All signatures include company LinkedIn and calendar booking links
- Banner can be updated independently without redistributing signatures