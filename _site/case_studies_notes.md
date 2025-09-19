# Case Studies & Project Notes

## Overview
Notes on old projects for potential case study content. Not for immediate website publication.

## Projects

### Alto Software Group (ASG) - Zendesk Instance Split
- **Client/Context:** Alto Software Group (part of Houseful/Zoopla ecosystem) - provides cloud CRM and property software for UK estate agents
- **Problem:** Monolithic legacy Zendesk instance serving both B2B (estate agents using Alto software) and B2C (Zoopla consumer portal) support needs required separation
- **Solution:** Complete configuration audit, brand mapping, and migration to separate Zendesk instances using custom tooling
- **Duration:** 6 weeks
- **Scale:** Dozens of triggers/automations, complex forms and ticket fields, numerous macros
- **Technologies:** Zendesk configuration management, custom tooling including Beacon, Salto.io
- **Challenges:**
  - Complex ticket field and form configurations requiring careful brand mapping
  - Trigger order conflicts with existing integrations
  - Hidden dependencies and negative brand conditions ("brand is not X")
  - Maintaining live B2B instance operation throughout migration process
- **Outcomes:** Successful separation of B2B and B2C support systems with minimal disruption
- **Key learnings:**
  - Complex legacy systems often have hidden dependencies and non-obvious brand relationships
  - Manual processes and insufficient documentation create significant migration complexity
  - Negative conditions ("brand is not X") can be particularly tricky to identify and migrate correctly
  - Trigger ordering can cause unexpected integration issues
  - Custom tooling essential for managing complex configuration migrations at scale

### Severn Trent Water - Fresh Zendesk Implementation
- **Client/Context:** Severn Trent Water supplier invoice processing team (~15 staff working shifts) handling invoices and regulatory communications
- **Problem:** Single shared Outlook mailbox with no automation, triaging, or proper reporting capabilities
- **Solution:** Complete Zendesk implementation with automated routing, invoice processing, and payment tracking
- **Duration:** 8 weeks
- **Technologies:** Zendesk, custom automation for attachment/invoice processing
- **Key features:**
  - Automated identification of attachments and invoice numbers
  - Priority domain routing to appropriate views for regulatory communications
  - Due date logging and payment term management
  - Payment terms configurable at organisation or user level
  - Automated application of payment terms to submitted invoices
- **Outcomes:** Shift-based team moved from manual Outlook process to automated, trackable system
- **Key learnings:**
  - Fresh implementations often simpler than complex migrations
  - Invoice processing requires careful automation around document identification
  - Different communication types (invoices vs regulatory) need separate handling workflows
  - Payment term flexibility essential for varied supplier relationships

## Ideas for Presentation
-
-
-

## Notes
-
-