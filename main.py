import os
import webapp2
import jinja2
import time
from datetime import datetime
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__),'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                                autoescape = True)

class BlogHandler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a,**kw)

    def render_str(self,template,**params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self,template,**kw):
        self.write(self.render_str(template,**kw))

def blog_key(name = 'default'):
    return db.Key.from_path('blogs',name)

class Blog(db.Model):
    title = db.StringProperty(required=True)
    blog = db.TextProperty(required=True)
    created = db.DateTimeProperty(required=True)

class BlogFront(BlogHandler):
    def render_front(self, title="", blog="", created="", error=""):
        blogs = db.GqlQuery("SELECT * FROM Blog ORDER BY created DESC LIMIT 5")
        self.render("front.html", title=title, blog=blog, created="", error=error, blogs=blogs)
    def get(self):
        self.render_front()

class NewPost(BlogHandler):
    def render_front(self, error="", entry_title="", entry_blog=""):
        self.render("newpost.html", error=error, entry_title=entry_title, entry_blog=entry_blog)

    def get(self):
        self.render("newpost.html", error="", entry_title="", entry_blog="")

    def post(self):
        title = self.request.get("title")
        blog = self.request.get("blog")
        created = datetime.today()
        entry_title = self.request.get('title')
        entry_blog = self.request.get('blog')

        if title and blog:
            a = Blog(title=title, blog=blog, created=created)
            a.put()
            time.sleep(1)
            self.redirect('/blog')
        else:
            error = "Please enter a title and blog content."
            self.render_front(error, entry_title, entry_blog)

class ViewPostHandler(BlogHandler):
    def render_blog(self, id=""):
        blogs = db.GqlQuery("SELECT * FROM Blog Where __key__ = KEY('Blog', " + id + ")"
                            " ORDER BY created DESC LIMIT 5")
        self.render("post.html", blogs=blogs, id=id)

    def get(self, id):
        self.render_blog(id)

app = webapp2.WSGIApplication([
    ('/blog', BlogFront),
    ('/newpost', NewPost),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler)
], debug=True)
