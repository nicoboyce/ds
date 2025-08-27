---
layout: page
title: "Visual Content and Media in Blog Posts"
date: 2025-08-26
background: grey
---

# Visual Lorem Ipsum

![Office Space](/assets/img/office.jpeg)
*Our office space in Southampton*

Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam, eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo.

## Images and Media

Nemo enim ipsam voluptatem quia voluptas sit aspernatur aut odit aut fugit, sed quia consequuntur magni dolores eos qui ratione voluptatem sequi nesciunt.

### Team Photos

![Team Member](/assets/img/team/rew.jpeg)

Neque porro quisquam est, qui dolorem ipsum quia dolor sit amet, consectetur, adipisci velit, sed quia non numquam eius modi tempora incidunt ut labore et dolore magnam aliquam quaerat voluptatem.

## Mixed Content

Ut enim ad minima veniam, quis nostrum exercitationem ullam corporis suscipit laboriosam, nisi ut aliquid ex ea commodi consequatur?

### Code with Context

Here's how we might process images in Python:

```python
from PIL import Image
import os

def optimise_images(directory):
    """
    Process images in a directory for web optimisation
    Lorem ipsum dolor sit amet implementation
    """
    for filename in os.listdir(directory):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            img_path = os.path.join(directory, filename)
            with Image.open(img_path) as img:
                # Resize if too large
                if img.width > 1200:
                    ratio = 1200 / img.width
                    new_height = int(img.height * ratio)
                    img = img.resize((1200, new_height), Image.Lanczos)
                
                # Save optimised version
                img.save(img_path, optimize=True, quality=85)
                print(f"Optimised: {filename}")

# Example usage
optimise_images("/assets/img/")
```

### Logo Showcase

![DS Logo](/assets/img/ds-logo-trans.svg)

At vero eos et accusamus et iusto odio dignissimos ducimus qui blanditiis praesentium voluptatum deleniti atque corrupti quos dolores et quas molestias excepturi sint occaecati cupiditate non provident.

## Timeline Content

![Showcase Image](/assets/img/timeline/showcase.jpeg)

Similique sunt in culpa qui officia deserunt mollitia animi, id est laborum et dolorum fuga. Et harum quidem rerum facilis est et expedita distinctio.

### Client Logos

Some of our fantastic clients:

![Checkout.com](/assets/img/logos/checkout_logo.jpg) ![Depop](/assets/img/logos/depop_logo.jpg)

Nam libero tempore, cum soluta nobis est eligendi optio cumque nihil impedit quo minus id quod maxime placeat facere possimus, omnis voluptas assumenda est, omnis dolor repellendus.

---

*Images optimised for web delivery • Published: 26th August 2025*