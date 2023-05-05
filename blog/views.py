from django.http import Http404
from django.shortcuts import render, get_object_or_404
from .models import Post, Comment
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import EmailPostForm, CommentForm
from django.core.mail import send_mail
from django.views.decorators.http import require_POST
# Create your views here.

def post_list(request):
  post_list = Post.published.all()
  # pagination with 3 posts per page
  paginator = Paginator(post_list, 3)
  page_number = request.GET.get('page', 1)
  try:
    posts = paginator.page(page_number)
  except PageNotAnInteger:
    # if page_number is not an interger, deliver first page
    posts = paginator.page(1)
  except EmptyPage:
    # if page_number is our of range, deliver result of last page
    posts = paginator.page(paginator.num_pages)
  return render(request, 'blog/post/list.html', {'posts': posts})

def post_detail(request, year, month, day, post):
  # try:
  #   post = Post.published.get(id=id)
  # except Post.DoesNotExist:
  #   raise Http404("No Post Found")

  post = get_object_or_404(Post, status=Post.Status.PUBLISHED, slug=post, publish__year=year, publish__month=month, publish__day=day)
  # List of active comments for this post
  comments = post.comments.filter(active=True)
  # Form for users to comment
  form = CommentForm()
  return render(request, 'blog/post/detail.html', {'post': post, 'comments': comments, 'form': form})

def post_share(request, post_id):
  # Retrieve the post by id
  post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
  if request.method == 'POST':
    # Form was submitted
    form = EmailPostForm(request.POST)
    if form.is_valid():
      # Form fields passed validation
      cd = form.cleaned_data
      # ... send Email
      post_url = request.build_absolute_uri(post.get_absolute_url())
      subject = f"{cd['name']} recomends you read " f"{post.title}"
      message = f"Read {post.title} ar {post_url}\n\n" \
                f"{cd['name']}\'s comments: {cd['comments']}"
      send_mail(subject, message, 'sinha.vikram3@gmail.com', [cd['to']])
      sent = True
  else:
    form = EmailPostForm()
    sent = False
  return render(request, 'blog/post/share.html', {'post': post, 'form': form, 'sent': sent})

@require_POST
def post_comment(request, post_id):
  post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
  comment = None
  # A Comment Was Posted
  form = CommentForm(data=request.POST)
  if form.is_valid():
    # Create a comment object without saving it to the Datebase
    comment = form.save(commit=False)
    # Assign the post to the comment
    comment.post = post
    # Save the comment to the Database
    comment.save()
  return render(request, 'blog/post/comment.html', {'post': post, 'form': form, 'comment': comment})
