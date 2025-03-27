# Stometa's Blog

This is the source code for my personal blog, built with [Hugo](https://gohugo.io/) and the [PaperMod](https://github.com/adityatelange/hugo-PaperMod) theme.

## Features

- Responsive design
- Dark/Light mode
- Search functionality
- Tags and categories
- Comments via Disqus
- Google Analytics

## Development

### Prerequisites

- [Hugo](https://gohugo.io/getting-started/installing/) (Extended version)
- Git

### Local Development

1. Clone the repository
   ```
   git clone git@github.com:stone16/HugoBlog.git
   cd HugoBlog
   ```

2. Start the local development server
   ```
   hugo server -D
   ```

3. Visit http://localhost:1313/ to see your site

### Creating Content

To create a new blog post:
```
hugo new content posts/my-new-post.md
```

## Deployment

The site is automatically deployed to GitHub Pages using GitHub Actions whenever changes are pushed to the main branch.

## License

This project is licensed under the MIT License. 