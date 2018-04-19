"""
    Routes
    ~~~~~~
"""
import os
from flask import Blueprint
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_login import current_user
from flask_login import login_required
from flask_login import login_user
from flask_login import logout_user

from wiki.core import Processor
from wiki.web.forms import EditorForm
from wiki.web.forms import LoginForm
from wiki.web.forms import SearchForm
from wiki.web.forms import CreateUserForm
from wiki.web.forms import DeleteUserForm
from wiki.web.forms import URLForm
from wiki.web import current_wiki
from wiki.web import current_users
from wiki.web.user import protect
from wiki.web import current_app
from csc440_albertm1_stage_a.user_createdelete import create_user
from csc440_albertm1_stage_a.user_createdelete import delete_user


bp = Blueprint('wiki', __name__)


@bp.route('/')
@protect
def home():
    page = current_wiki.get('home')
    if page:
        return display('home')
    return render_template('home.html')


@bp.route('/index/')
@protect
def index():
    pages = current_wiki.index()
    return render_template('index.html', pages=pages)


@bp.route('/<path:url>/')
@protect
def display(url):
    page = current_wiki.get_or_404(url)
    return render_template('page.html', page=page)


@bp.route('/create/', methods=['GET', 'POST'])
@protect
def create():
    form = URLForm()
    if form.validate_on_submit():
        return redirect(url_for(
            'wiki.edit', url=form.clean_url(form.url.data)))
    return render_template('create.html', form=form)


@bp.route('/edit/<path:url>/', methods=['GET', 'POST'])
@protect
def edit(url):
    page = current_wiki.get(url)
    form = EditorForm(obj=page)
    if form.validate_on_submit():
        if not page:
            page = current_wiki.get_bare(url)
        form.populate_obj(page)
        page.save()
        flash('"%s" was saved.' % page.title, 'success')
        return redirect(url_for('wiki.display', url=url))
    return render_template('editor.html', form=form, page=page)


@bp.route('/preview/', methods=['POST'])
@protect
def preview():
    data = {}
    processor = Processor(request.form['body'])
    data['html'], data['body'], data['meta'] = processor.process()
    return data['html']


@bp.route('/move/<path:url>/', methods=['GET', 'POST'])
@protect
def move(url):
    page = current_wiki.get_or_404(url)
    form = URLForm(obj=page)
    if form.validate_on_submit():
        newurl = form.url.data
        current_wiki.move(url, newurl)
        return redirect(url_for('wiki.display', url=newurl))
    return render_template('move.html', form=form, page=page)


@bp.route('/delete/<path:url>/')
@protect
def delete(url):
    page = current_wiki.get_or_404(url)
    current_wiki.delete(url)
    flash('Page "%s" was deleted.' % page.title, 'success')
    return redirect(url_for('wiki.home'))


@bp.route('/tags/')
@protect
def tags():
    tags = current_wiki.get_tags()
    return render_template('tags.html', tags=tags)


@bp.route('/tag/<string:name>/')
@protect
def tag(name):
    tagged = current_wiki.index_by_tag(name)
    return render_template('tag.html', pages=tagged, tag=name)


@bp.route('/search/', methods=['GET', 'POST'])
@protect
def search():
    form = SearchForm()
    if form.validate_on_submit():
        results = current_wiki.search(form.term.data, form.ignore_case.data)
        return render_template('search.html', form=form,
                               results=results, search=form.term.data)
    return render_template('search.html', form=form, search=None)


@bp.route('/user/login/', methods=['GET', 'POST'])
def user_login():
    form = LoginForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            user = current_users.get_user(form.name.data)
            login_user(user)
            user.set('authenticated', True)
            if user.get('authenticated') is True:
                print("User authentication worked!")
            flash('Login successful.', 'success')
            return redirect(request.args.get("next") or url_for('wiki.index'))
    return render_template('login.html', form=form)


@bp.route('/user/logout/')
@login_required
def user_logout():
    current_user.set('authenticated', False)
    logout_user()
    flash('Logout successful.', 'success')
    return redirect(url_for('wiki.index'))


@bp.route('/user/')
def user_index():
    pass


@bp.route('/user/create/', methods=['GET', 'POST'])
def user_create():
    form = CreateUserForm(request.form)
    if request.method == 'POST':
        user = create_user(form, os.path.join(current_app.config["USER_DIR"], 'users.json'), 'cleartext')
        if not user:
            flash('Failed to create user', 'failure')
            return redirect(url_for('wiki.user_create'))
        flash('Created new user!', 'success')
        return redirect(url_for('wiki.index'))
        #if form.validate_on_submit():
        #    user = current_users.add_user(form.name.data, form.password.data)
        #    if not user:
        #        flash('Failed to create user.', 'failure')
        #        return redirect(url_for('wiki.user_create'))
        #    flash('Created new user!', 'success')
        #    return redirect(url_for('wiki.index'))
    return render_template('createuser.html', form=form)


@bp.route('/user/<int:user_id>/')
def user_admin(user_id):
    pass


@bp.route('/user/delete', methods=['GET', 'POST'])
@login_required
def user_delete_list():
    results = current_users.read()
    return render_template('deletelist.html', results=results)



@bp.route('/user/delete/<string:user_id>', methods=['GET', 'POST'])
@login_required
def user_delete(user_id):
    form = DeleteUserForm(request.form)
    if request.method == 'POST':
        #usercheck = current_users.get_user(user_id)
        response = delete_user(form, os.path.join(current_app.config["USER_DIR"], 'users.json'), user_id)
        if not response:
            flash('Failed to delete user.', 'failure')
            return redirect(url_for('wiki.index'))
        flash('Successfully deleted user.', 'success')
        return redirect(url_for('wiki.index'))
        #if form.validate_on_submit():
            #if usercheck.get("password") == form.id.data:
                #user = current_users.delete_user(user_id)
                #if not user:
                    #flash('Failed to delete user.', 'failure')
                    #return redirect(url_for('wiki.index'))
                #flash('Successfully deleted user.', 'success')
                #return redirect(url_for('wiki.index'))
    return render_template('deleteuser.html', form=form, UID=user_id)


"""
    Error Handlers
    ~~~~~~~~~~~~~~
"""


@bp.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

