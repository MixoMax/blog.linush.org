from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import sys
import os
import markdown
from markdown.extensions import codehilite, toc, tables, fenced_code, footnotes
import frontmatter
from datetime import datetime
from typing import List, Dict, Any
import re
from pathlib import Path

app = FastAPI(title="Blog Server", description="A professional blog server with markdown support")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Markdown configuration with extensions
def get_markdown_processor():
    return markdown.Markdown(extensions=[
        'codehilite',
        'toc',
        'tables',
        'fenced_code',
        'footnotes',
        'attr_list',
        'def_list',
        'abbr',
        'nl2br',
        'sane_lists',
        'smarty',
        'wikilinks',
        'meta'
    ], extension_configs={
        'codehilite': {
            'css_class': 'highlight',
            'use_pygments': True,
            'noclasses': True
        },
        'toc': {
            'permalink': True,
            'permalink_class': 'toc-link',
            'permalink_title': 'Link to this section'
        }
    })

def process_markdown_file(file_path: str) -> Dict[str, Any]:
    """Process a markdown file and return metadata and HTML content."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File {file_path} not found")
    print(f"[DEBUG]: Processing markdown file {file_path}")
    #with open(file_path, 'r', encoding='utf-8') as f:
    post = frontmatter.parse(file_path)
    print("[DEBUG]: frontmatter parsed")
    
    md = get_markdown_processor()
    html_content = md.convert(post["content"])
    print("[DEBUG]: markdown converted to HTML")
    
    # Extract metadata
    metadata = post["metadata"]
    print(f"[DEBUG]: metadata extracted: {metadata}")
    
    # Get file stats for date if not in frontmatter
    file_stat = os.stat(file_path)
    created_date = datetime.fromtimestamp(file_stat.st_ctime)
    modified_date = datetime.fromtimestamp(file_stat.st_mtime)
    print(f"[DEBUG]: file stats - created: {created_date}, modified: {modified_date}")
    
    return {
        'title': metadata.get('title', os.path.basename(file_path).replace('.md', '').replace('_', ' ').title()),
        'content': html_content,
        'toc': md.toc if hasattr(md, 'toc') else '',
        'meta': md.Meta if hasattr(md, 'Meta') else {},
        'created_date': metadata.get('date', created_date),
        'modified_date': modified_date,
        'author': metadata.get('author', 'Anonymous'),
        'description': metadata.get('description', ''),
        'tags': metadata.get('tags', []),
        'filename': os.path.basename(file_path).replace('.md', '')
    }

def get_all_blog_posts() -> List[Dict[str, Any]]:
    """Get all blog posts from the blog_src directory."""
    print("[DEBUG]: Getting all blog posts")
    blog_posts = []
    blog_src_dir = Path('blog_src')
    
    if not blog_src_dir.exists():
        print("[DEBUG]: blog_src directory does not exist")
        return []
    
    for md_file in blog_src_dir.glob('*.md'):
        try:
            print(f"[DEBUG]: Processing file {md_file}")
            post_data = process_markdown_file(str(md_file))
            print(f"[DEBUG]: Processed post data: {post_data['title']}")
            blog_posts.append(post_data)
        except Exception as e:
            print(f"Error processing {md_file}: {e}")
    
    # Sort by creation date (newest first)
    blog_posts.sort(key=lambda x: x['created_date'], reverse=True)
    print(f"[DEBUG]: Total blog posts found: {len(blog_posts)}")
    return blog_posts

def create_blog_html(post_data: Dict[str, Any]) -> str:
    """Create a complete HTML page for a blog post using a template file."""
    template_path = "templates/blog_template.html"
    with open(template_path, "r", encoding="utf-8") as f:
        template = f.read()

    # Prepare replacements
    replacements = {
        "{{title}}": post_data["title"],
        "{{author}}": post_data["author"],
        "{{created_date}}": post_data["created_date"].strftime("%B %d, %Y"),
        "{{description}}": post_data["description"],
        "{{content}}": post_data["content"],
        "{{toc}}": (
            f'<div class="table-of-contents"><h3>Table of Contents</h3>{post_data["toc"]}</div>'
            if post_data["toc"] else ""
        ),
        "{{tags}}": (
            '<div class="post-tags">' +
            "".join([f'<a href="/tag/{tag}" class="tag">{tag}</a>' for tag in post_data["tags"]]) +
            '</div>' if post_data["tags"] else ""
        ),
    }

    # Replace placeholders
    for key, value in replacements.items():
        template = template.replace(key, value)

    return template

@app.get("/", response_class=HTMLResponse)
async def home():
    """Serve the homepage."""
    return FileResponse("static/index.html")

@app.get("/blog/{filename}")
async def get_blog_post(filename: str):
    """Get a specific blog post by filename."""
    file_path = f"blog_src/{filename}.md"
    
    try:
        post_data = process_markdown_file(file_path)
        return HTMLResponse(create_blog_html(post_data))
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Blog post not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing blog post: {str(e)}")

@app.get("/blogs")
async def get_all_blogs_page():
    """Get a page with all blog posts using a template."""
    posts = get_all_blog_posts()

    blog_cards = ""
    for post in posts:
        card = '<div class="blog-card">'
        card += f'<h2><a href="/blog/{post["filename"]}">{post["title"]}</a></h2>'
        card += '<div class="post-meta">'
        card += f'<span>By {post["author"]}</span>'
        card += f'<span>{post["created_date"].strftime("%B %d, %Y")}</span>'
        card += '</div>'
        if post["description"]:
            card += f'<p class="post-description">{post["description"]}</p>'
        if post["tags"]:
            card += '<div class="post-tags">'
            card += "".join([f'<a href="/tag/{tag}" class="tag">{tag}</a>' for tag in post["tags"]])
            card += '</div>'
        card += '</div>'
        blog_cards += card

    with open("templates/blog_list_template.html", "r", encoding="utf-8") as f:
        template = f.read()

    replacements = {
        "{{title}}": "All Posts",
        "{{header}}": "All Blog Posts",
        "{{blog_cards}}": blog_cards,
    }

    for key, value in replacements.items():
        template = template.replace(key, value)

    return HTMLResponse(template)

@app.get("/tag/{tag_name}")
async def get_posts_by_tag(tag_name: str):
    """Get all blog posts that have the specified tag using a template."""
    all_posts = get_all_blog_posts()
    tagged_posts = [post for post in all_posts if tag_name.lower() in [tag.lower() for tag in post['tags']]]

    blog_cards = ""
    if not tagged_posts:
        blog_cards = (
            f'<div class="no-posts">'
            f'<h2>No posts found with tag "{tag_name}"</h2>'
            f'<p><a href="/blogs">View all posts</a> or <a href="/">return to homepage</a></p>'
            f'</div>'
        )
        description = ""
    else:
        for post in tagged_posts:
            card = '<div class="blog-card">'
            card += f'<h2><a href="/blog/{post["filename"]}">{post["title"]}</a></h2>'
            card += '<div class="post-meta">'
            card += f'<span>By {post["author"]}</span>'
            card += f'<span>{post["created_date"].strftime("%B %d, %Y")}</span>'
            card += '</div>'
            if post["description"]:
                card += f'<p class="post-description">{post["description"]}</p>'
            if post["tags"]:
                card += '<div class="post-tags">'
                card += "".join([f'<a href="/tag/{tag}" class="tag">{tag}</a>' for tag in post["tags"]])
                card += '</div>'
            card += '</div>'
            blog_cards += card
        description = f'Showing {len(tagged_posts)} post{"s" if len(tagged_posts) != 1 else ""} with this tag'

    with open("templates/tag_list_template.html", "r", encoding="utf-8") as f:
        template = f.read()

    replacements = {
        "{{title}}": f'Posts tagged "{tag_name}"',
        "{{header}}": f'Posts tagged "{tag_name}"',
        "{{description}}": description,
        "{{blog_cards}}": blog_cards,
        "{{section_footer}}": '<a href="/blogs" class="btn btn-outline">View All Posts</a>',
    }

    for key, value in replacements.items():
        template = template.replace(key, value)

    return HTMLResponse(template)

# API Routes
@app.get("/api/posts")
async def get_posts_api():
    """API endpoint to get all blog posts."""
    posts = get_all_blog_posts()
    
    # Return simplified data for API
    api_posts = []
    for post in posts:
        api_posts.append({
            'title': post['title'],
            'filename': post['filename'],
            'author': post['author'],
            'created_date': post['created_date'].isoformat(),
            'description': post['description'],
            'tags': post['tags']
        })
    
    return JSONResponse(content={"posts": api_posts})

@app.get("/api/posts/latest")
async def get_latest_posts_api(limit: int = 5):
    """API endpoint to get the latest blog posts."""
    posts = get_all_blog_posts()[:limit]
    
    api_posts = []
    for post in posts:
        api_posts.append({
            'title': post['title'],
            'filename': post['filename'],
            'author': post['author'],
            'created_date': post['created_date'].isoformat(),
            'description': post['description'],
            'tags': post['tags']
        })
    
    return JSONResponse(content={"posts": api_posts})

@app.get("/api/posts/{filename}")
async def get_post_api(filename: str):
    """API endpoint to get a specific blog post."""
    file_path = f"blog_src/{filename}.md"
    
    try:
        post_data = process_markdown_file(file_path)
        return JSONResponse(content={
            'title': post_data['title'],
            'content': post_data['content'],
            'author': post_data['author'],
            'created_date': post_data['created_date'].isoformat(),
            'description': post_data['description'],
            'tags': post_data['tags'],
            'toc': post_data['toc']
        })
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Blog post not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing blog post: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return JSONResponse(status_code=200, content={"status": "ok"})

# Fallback for static files
@app.get("/{path:path}")
async def serve_static_file(path: str):
    """Serve static files as fallback."""
    if path == "":
        return await home()
    
    file_path = os.path.join("static", path)
    
    if os.path.exists(file_path):
        return FileResponse(file_path)
    else:
        raise HTTPException(status_code=404, detail="File not found")

if __name__ == "__main__":
    port = 8000
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    uvicorn.run(app, host="0.0.0.0", port=port)
