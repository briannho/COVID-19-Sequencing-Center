import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from flaskDemo import app, db, bcrypt
from flaskDemo.forms import RegistrationForm, LoginForm, UpdateAccountForm, AuthorForm, AuthorUpdateForm, SequenceForm, SequenceUpdateForm, OrganismForm, OrganismUpdateForm, PublicationForm, PublicationUpdateForm, AssignForm, AssignUpdateForm
from flaskDemo.models import User, Author, School, Publication, Author_Publications, Organism, Journal, Sequence, Seq_Type
from flask_login import login_user, current_user, logout_user, login_required
from datetime import datetime

@app.route("/")
@app.route("/home")
def home():

    sql = 'SELECT author.FirstName, author.LastName, publication.Title, publication.PubDate ' + \
    'FROM author, publication, author_publications WHERE author.AuthorID = author_publications.AuthorID ' +\
    'AND publication.PubID = author_publications.PubId ORDER BY publication.PubDate DESC'
    query_out = db.engine.execute(sql)
    results_1 = [dict(row) for row in query_out]

    new_results = []

    for entry in results_1:
        new_entry = {}

        if not any(d['Title'] == entry["Title"] for d in new_results):
            new_entry["Title"] = entry["Title"]
            new_entry["Authors"] = entry["FirstName"] + " " + entry["LastName"]
            new_entry["PubDate"] = entry["PubDate"]
            new_results.append(new_entry)
        else:
            for d in new_results:
                if d["Title"] == entry["Title"]:
                    d["Authors"] = d["Authors"] + ", " + entry["FirstName"] + " " + entry["LastName"]

    return render_template('home.html', results = new_results)

@app.route("/about")
def about():
    return render_template('about.html', title = 'About')

@app.route("/register", methods = ['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username = form.username.data, email = form.email.data, password = hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title = 'Register', form = form)

@app.route("/login", methods = ['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember = form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title = 'Login', form = form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn

@app.route("/account", methods = ['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename = 'profile_pics/' + current_user.image_file)
    return render_template('account.html', title = 'Account',
                           image_file = image_file, form = form)

##################################################################################
#JOURNAL ROUTE
##################################################################################

#main page
@app.route("/journals")
def journals():

    results = Journal.query.all()
    return render_template('journals.html', title = 'Journals', results = results)

#view page
@app.route("/journals/<JournalID>")
def journal(JournalID):
    journal = Journal.query.get_or_404(JournalID)
    results = Publication.query.filter_by(JournalID = JournalID).all()
    return render_template('journal.html', title = journal.JournalID, journal = journal, results=results)

##################################################################################
#AUTHOR ROUTES
##################################################################################

#main page
@app.route("/authors")
def authors():

    print("Query to select all columns from the Author table")
    sql = 'SELECT * FROM Author'
    query_out = db.engine.execute(sql)
    result = [dict(row) for row in query_out]

    for entry in result:
        print(entry)

    print("\nQuery to select the first and last name of all authors who go to school not in the USA")
    sql = "SELECT FirstName, LastName FROM Author WHERE Author.SchoolID IN (SELECT School.SchoolID FROM School WHERE SchoolCountry != 'USA')"
    query_out = db.engine.execute(sql)
    result = [dict(row) for row in query_out]

    for entry in result:
        print(entry)

    sql = 'SELECT * FROM Author NATURAL JOIN School ORDER BY Author.LastName'
    query_out = db.engine.execute(sql)
    results = [dict(row) for row in query_out]

    return render_template('authors.html', title = 'Authors', results = results)

#update/delete page
@app.route("/authors/<AuthorID>")
@login_required
def author(AuthorID):
    author = Author.query.get_or_404(AuthorID)
    return render_template('author.html', title = author.AuthorID, author = author, now = datetime.utcnow())

#route for creating
@app.route("/authors/new", methods = ['GET', 'POST'])
@login_required
def new_author():

    form = AuthorForm()
    if form.validate_on_submit():
        author = Author(AuthorID = form.AuthorID.data, FirstName = form.FirstName.data, LastName = form.LastName.data, SchoolID = form.SchoolID.data)
        db.session.add(author)
        db.session.commit()
        flash('You have added a new author!', 'success')
        return redirect(url_for('authors'))

    return render_template('create_author.html', title = 'New Author',
                           form = form, legend = 'New Author')

#route for updating
@app.route("/authors/<AuthorID>/update", methods = ['GET', 'POST'])
@login_required
def update_author(AuthorID):

    author = Author.query.get_or_404(AuthorID)
    form = AuthorUpdateForm()
    if form.validate_on_submit():
        author.FirstName = form.FirstName.data
        author.LastName = form.LastName.data
        author.SchoolID = form.SchoolID.data
        db.session.commit()
        flash('The author has been updated!', 'success')
        return redirect(url_for('author', AuthorID = AuthorID))

    elif request.method == 'GET':
        form.AuthorID.data = author.AuthorID
        form.FirstName.data = author.FirstName
        form.LastName.data = author.LastName
        form.SchoolID.data = author.SchoolID
    return render_template('create_author.html', title = 'Update Author',
                           form = form, legend = 'Update Author')

#route for deleting
@app.route("/authors/<AuthorID>/delete", methods = ['POST'])
@login_required
def delete_author(AuthorID):

    try:
        author = Author.query.get_or_404(AuthorID)
        db.session.delete(author)
        db.session.commit()
        flash('This Author has been removed.', 'success')
        return redirect(url_for('authors'))

    except:
        flash("Please delete all assignments linked with this author first!", "danger")

    return redirect(url_for('author', AuthorID = AuthorID))

##################################################################################
#SEQUENCES ROUTES
##################################################################################

#main page
@app.route("/sequencebank")
def sequencebank():

    sql = "SELECT O.Genus, O.Subgenus, S.AccessionID, S.SeqDate, S.SeqType, S.Seq " \
          "FROM Sequence S, Organism O WHERE S.OrganismID = O.OrganismID ORDER BY S.SeqDate DESC"
    query_out = db.engine.execute(sql)
    results_sql = [dict(row) for row in query_out]

    return render_template('sequencebank.html', title='Sequence Databank', results = results_sql)

#update/delete page
@app.route("/sequencebank/<AccessionID>")
def sequence(AccessionID):
    sequence = Sequence.query.get_or_404(AccessionID)
    return render_template('sequence.html', title = sequence.AccessionID, sequence = sequence, now = datetime.utcnow())

#route for creating
@app.route("/sequencebank/new", methods = ['GET', 'POST'])
@login_required
def new_sequence():

    form = SequenceForm()
    if form.validate_on_submit():
        sequence = Sequence(AccessionID = form.AccessionID.data, Seq = form.Seq.data, SeqType = form.SeqType.data, SeqCountry = form.SeqCountry.data, \
                        OrganismID = form.OrganismID.data, SeqDate = form.SeqDate.data)
        db.session.add(sequence)
        db.session.commit()
        flash('You have uploaded a new sequence!', 'success')
        return redirect(url_for('sequencebank'))

    return render_template('create_sequence.html', title = 'New Sequence', form=form, legend = 'New Sequence')

#route for updating
@app.route("/sequencebank/<AccessionID>/update", methods = ['GET', 'POST'])
@login_required
def update_sequence(AccessionID):

    sequence = Sequence.query.get_or_404(AccessionID)
    form = SequenceUpdateForm()
    if form.validate_on_submit():
        sequence.Seq = form.Seq.data
        sequence.SeqType = form.SeqType.data
        sequence.SeqCountry = form.SeqCountry.data
        sequence.OrganismID = form.OrganismID.data
        sequence.SeqDate = form.SeqDate.data
        db.session.commit()
        flash('The sequence has been updated!', 'success')
        return redirect(url_for('sequence', AccessionID = AccessionID))

    elif request.method == 'GET':
        form.AccessionID.data = sequence.AccessionID
        form.Seq.data = sequence.Seq
        form.SeqType.data = sequence.SeqType
        form.SeqCountry.data = sequence.SeqCountry
        form.OrganismID.data = sequence.OrganismID
        form.SeqDate.data = sequence.SeqDate
    return render_template('create_sequence.html', title = 'Update Sequence', form = form, legend = 'Update Sequence')

#route for deleting
@app.route("/sequencebank/<AccessionID>/delete", methods = ['POST'])
@login_required
def delete_sequence(AccessionID):
    try:
        sequence = Sequence.query.get_or_404(AccessionID)
        db.session.delete(sequence)
        db.session.commit()
        flash('This sequence has been removed.', 'success')
    except:
        flash('Unable to remove sequence. Please remove associated publication first.', 'danger')

    return redirect(url_for('sequencebank'))

##################################################################################
#ORGANISM ROUTES
##################################################################################

#main page
@app.route("/organisms")
def organisms():

    results = Organism.query.order_by(Organism.Genus,Organism.Subgenus).all()
    return render_template('organisms.html', title = 'List of Organisms', results = results)

#update/delete page
@app.route("/organisms/<OrganismID>")
@login_required
def organism(OrganismID):
    organism = Organism.query.get_or_404(OrganismID)
    return render_template('organism.html', title = organism.OrganismID, organism = organism, now = datetime.utcnow())

#route for creating
@app.route("/organisms/new", methods = ['GET', 'POST'])
@login_required
def new_organism():

    form = OrganismForm()
    if form.validate_on_submit():
        organism = Organism(OrganismID = form.OrganismID.data, Genus = form.Genus.data, Subgenus = form.Subgenus.data)
        db.session.add(organism)
        db.session.commit()
        flash('You have added a new organism!', 'success')
        return redirect(url_for('organisms'))

    return render_template('create_organism.html', title = 'New Organism', form = form, legend = 'New Organism')

#route for updating
@app.route("/organisms/<OrganismID>/update", methods = ['GET', 'POST'])
@login_required
def update_organism(OrganismID):

    organism = Organism.query.get_or_404(OrganismID)
    form = OrganismUpdateForm()
    if form.validate_on_submit():
        organism.Genus = form.Genus.data
        organism.Subgenus = form.Subgenus.data
        db.session.commit()
        flash('The organism has been updated!', 'success')
        return redirect(url_for('organism', OrganismID = OrganismID))

    elif request.method == 'GET':
        form.OrganismID.data = organism.OrganismID
        form.Genus.data = organism.Genus
        form.Subgenus.data = organism.Subgenus
    return render_template('create_organism.html', title = 'Update Organism', form = form, legend = 'Update Organism')

#route for deleting
@app.route("/organisms/<OrganismID>/delete", methods = ['POST'])
@login_required
def delete_organism(OrganismID):
    organism = Organism.query.get_or_404(OrganismID)

    try:
        db.session.delete(organism)
        db.session.commit()
        flash('This organism has been removed.', 'success')
        return redirect(url_for('organisms'))
    except:
        flash("Unable to delete organism from database because it is registered in the sequence databank.", "danger")

    return redirect(url_for('organism', OrganismID = OrganismID))

##################################################################################
#PUBLICATION ROUTES
##################################################################################

#main page
@app.route("/publications")
def publications():
    sql = 'SELECT COUNT(*) FROM Publication'
    query_out = db.engine.execute(sql)
    result = [dict(row) for row in query_out]
    total = result[0]['COUNT(*)']

    results = Publication.query.order_by(Publication.PubDate.desc()).distinct()
    return render_template('publications.html', title = 'Publications', results = results, total = total)

#update/delete page
@app.route("/publications/<PubID>")
def publication(PubID):
    publication = Publication.query.get_or_404(PubID)
    return render_template('publication.html', title = publication.PubID, publication = publication, now = datetime.utcnow())

#route for creating
@app.route("/publications/new", methods = ['GET', 'POST'])
@login_required
def new_publication():

    form = PublicationForm()
    if form.validate_on_submit():
        publication = Publication(PubID = form.PubID.data, Title = form.Title.data, AccessionID = form.AccessionID.data, JournalID = form.JournalID.data, \
                        PubDate = form.PubDate.data, Summary = form.Summary.data)
        db.session.add(publication)
        db.session.commit()
        flash('You have submitted a new publication!', 'success')
        return redirect(url_for('publications'))

    return render_template('create_publication.html', title = 'New Publication', form = form, legend = 'New Publication')

#route for updating
@app.route("/publications/<PubID>/update", methods = ['GET', 'POST'])
@login_required
def update_publication(PubID):

    publication = Publication.query.get_or_404(PubID)
    form = PublicationUpdateForm()
    if form.validate_on_submit():
        publication.Title = form.Title.data
        publication.Summary = form.Summary.data
        db.session.commit()
        flash('The publication has been updated!', 'success')
        return redirect(url_for('publication', PubID = PubID))

    elif request.method == 'GET':
        form.PubID.data = publication.PubID
        form.Title.data = publication.Title
        form.Summary.data = publication.Summary
    return render_template('create_publication.html', title = 'Update Publication', form = form, legend = 'Update Publication')

#route for deleting
@app.route("/publication/<PubID>/delete", methods = ['POST'])
@login_required
def delete_publication(PubID):

    try:
        publication = Publication.query.get_or_404(PubID)
        db.session.delete(publication)
        db.session.commit()
        flash('This publication has been removed.', 'success')
        return redirect(url_for('publications'))

    except:
        flash("Please delete all assignments linked with this publication first!", "danger")

    return redirect(url_for('publication', PubID = PubID))

##################################################################################
#ASSIGNMENT ROUTES
##################################################################################

#main page
@app.route("/assignments")
def assignments():

    results = Author_Publications.query.join(Author, Author_Publications.AuthorID == Author.AuthorID) \
                .join(Publication, Author_Publications.PubID == Publication.PubID) \
                .add_columns(Author.FirstName, Author.LastName, Publication.Title, Author_Publications.PubID, Author_Publications.AuthorID)

    return render_template('assignments.html', title='Assignments', results = results)

#update/delete page
@app.route("/assignments/<PubID>/<AuthorID>")
def assignment(PubID,AuthorID):
    assignment = Author_Publications.query.get_or_404([PubID,AuthorID])
    return render_template('assignment.html', title = str(assignment.PubID) + ": " + str(assignment.AuthorID), assignment = assignment, now = datetime.utcnow())

#route for creating
@app.route("/assignments/new", methods = ['GET', 'POST'])
@login_required
def new_author_publication():

    form = AssignForm()
    try:

        if form.validate_on_submit():
            author_publication = Author_Publications(PubID = form.PubID.data, AuthorID = form.AuthorID.data)
            db.session.add(author_publication)
            db.session.commit()
            flash('You have submitted a new assignment!', 'success')
            return redirect(url_for('home'))

    except:
        flash("This person is already an author of this paper. Please try again.", "danger")

    return render_template('create_author_publication.html', title = 'New Assignment', form = form, legend = 'New Assignment')

#route for updating
@app.route("/assignments/<PubID>/<AuthorID>/update", methods = ['GET', 'POST'])
@login_required
def update_assignment(PubID,AuthorID):

    assignment = Author_Publications.query.get_or_404([PubID,AuthorID])
    form = AssignUpdateForm()
    if form.validate_on_submit():
        assignment.PubID = form.PubID.data
        assignment.AuthorID = form.AuthorID.data
        db.session.commit()
        flash('The assignment has been updated!', 'success')
        return redirect(url_for('assignment',PubID = assignment.PubID,AuthorID = assignment.AuthorID))

    elif request.method == 'GET':
        form.PubID.data = assignment.PubID
        form.AuthorID.data = assignment.AuthorID
    return render_template('create_author_publication.html', title = 'Update Assignment', form = form, legend = 'Update Assignment')

#route for deleting
@app.route("/assignments/<PubID>/<AuthorID>/delete", methods = ['POST'])
@login_required
def delete_assignment(PubID,AuthorID):
    assignment = Author_Publications.query.get_or_404([PubID,AuthorID])
    db.session.delete(assignment)
    db.session.commit()
    flash('This pairing has been removed.', 'success')
    return redirect(url_for('assignments'))