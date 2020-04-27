from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, IntegerField, DateField, SelectField, HiddenField, DecimalField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError,Regexp
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from flaskDemo import db
from flaskDemo.models import User, Author, Author_Publications, Publication, Journal, School, Organism, Sequence, Seq_Type
from wtforms.fields.html5 import DateField

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators = [DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators = [DataRequired(), Email()])
    password = PasswordField('Password', validators = [DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators = [DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username = username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email = email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators = [DataRequired(), Email()])
    password = PasswordField('Password', validators = [DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class UpdateAccountForm(FlaskForm):
    username = StringField('Username', validators = [DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators = [DataRequired(), Email()])
    picture = FileField('Update Profile Picture', validators = [FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username = username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email = email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')

class AuthorUpdateForm(FlaskForm):

    #fields
    AuthorID = HiddenField("")
    FirstName = StringField('First Name:', validators = [DataRequired(), Length(max=50)])
    LastName = StringField('Last Name:', validators = [DataRequired(), Length(max=50)])
    SchoolID = SelectField("School:", coerce=int)
    submit = SubmitField('Update Author')

    #ensure dynamic select fields
    def __init__(self, *args, **kwargs):
        super(AuthorUpdateForm, self).__init__(*args, **kwargs)

        #retrieve school IDs
        self.SchoolID.choices = [(row.SchoolID, row.SchoolName) for row in School.query.with_entities(School.SchoolID, School.SchoolName)]

class AuthorForm(AuthorUpdateForm):

    AuthorID = IntegerField('Author ID', validators = [DataRequired()])
    submit = SubmitField('Add Author')

    def validate_AuthorID(self, AuthorID):
        author = Author.query.filter_by(AuthorID = AuthorID.data).first()
        if author:
            raise ValidationError('That Author ID is taken. Please choose a different one.')

##################################################################################

class OrganismUpdateForm(FlaskForm):

    OrganismID = HiddenField("")
    Genus = StringField('Genus:', validators = [DataRequired(), Length(max=30)])
    Subgenus = StringField('Subgenus:', validators = [Length(max=30)])
    submit = SubmitField('Update Organism')

class OrganismForm(OrganismUpdateForm):

    OrganismID = IntegerField('Organism ID:', validators = [DataRequired()])
    submit = SubmitField('Submit Organism')

    def validate_OrganismID(self, OrganismID):
        organism = Organism.query.filter_by(OrganismID = OrganismID.data).first()
        if organism:
            raise ValidationError('That Organism ID is taken. Please choose a different one.')

##################################################################################

class SequenceUpdateForm(FlaskForm):

    AccessionID = HiddenField("")
    SeqType = SelectField('Sequence Type:')
    Seq = StringField('Paste sequence here:', validators = [DataRequired()])
    OrganismID = SelectField('Organism:', coerce=int)
    SeqCountry = StringField('Country of Origin:', validators = [Length(max=50)])
    SeqDate = DateField("Date of Submission:", format='%Y-%m-%d')
    submit = SubmitField('Update Sequence')

    #ensure dynamic select fields
    def __init__(self, *args, **kwargs):
        super(SequenceUpdateForm, self).__init__(*args, **kwargs)

        #retrieve organism IDs
        self.OrganismID.choices = [(row.OrganismID, row.Genus + ' ' + row.Subgenus)
                                  for row in Organism.query.with_entities(Organism.OrganismID, Organism.Genus, Organism.Subgenus)]
        #retrieve sequence types
        self.SeqType.choices = [(row.type,row.type) for row in Seq_Type.query.with_entities(Seq_Type.type)]

class SequenceForm(SequenceUpdateForm):

    AccessionID = StringField('Accession ID', validators = [DataRequired(), Length(max=30), Regexp('[A-Z][A-Z)][0-9]{6,6}', \
    				message = 'An Accession ID starts with any two characters A-Z, and then six digits 0-9.')])
    submit = SubmitField('Submit Sequence')

    def validate_AccessionID(self, AccessionID):
        sequence = Sequence.query.filter_by(AccessionID = AccessionID.data).first()
        if sequence:
            raise ValidationError('That Accession ID is taken. Please choose a different one.')

##################################################################################

class PublicationUpdateForm(FlaskForm):

    PubID = HiddenField("")
    Title = StringField('Title:', validators = [DataRequired(), Length(max=200)])
    AccessionID = HiddenField("")
    JournalID = HiddenField("")
    PubDate = DateField("Date of Publication:", format='%Y-%m-%d')
    Summary = StringField('Summary:')
    submit = SubmitField('Update Publication')

class PublicationForm(PublicationUpdateForm):

    PubID = IntegerField('Publication ID:', validators = [DataRequired()])
    AccessionID = SelectField('Accession ID:')
    JournalID = SelectField('Journal:', coerce=int)
    submit = SubmitField('Submit Publication')

    def validate_PubID(self, PubID):
        publication = Publication.query.filter_by(PubID = PubID.data).first()
        if publication:
            raise ValidationError('That Publication ID is taken. Please choose a different one.')

     #ensure dynamic select fields
    def __init__(self, *args, **kwargs):
        super(PublicationForm, self).__init__(*args, **kwargs)

        #retrieve accession IDs
        self.AccessionID.choices = [(row.AccessionID, row.AccessionID) for row in Sequence.query.with_entities(Sequence.AccessionID)]

        #retrieve journal IDS
        self.JournalID.choices = [(row.JournalID, row.JournalName) for row in Journal.query.with_entities(Journal.JournalID, Journal.JournalName)]

##################################################################################

class AssignUpdateForm(FlaskForm):
 
    PubID = SelectField('Publication ID:', coerce=int)
    AuthorID = SelectField('Author:', coerce=int)
    submit = SubmitField('Update Assignment')

    def validate_pairing(self, PubID, AuthorID):    # cannot have repeat of author and pub pair
         pair = Department.query.filter_by(PubID = PubID.data, AuthorID = AuthorID.data).first()
         if pair:
             raise ValidationError('This person is already an author of this paper. Please try again.')

    #ensure dynamic select fields
    def __init__(self, *args, **kwargs):
        super(AssignUpdateForm, self).__init__(*args, **kwargs)

        #retrieve publication IDs
        self.PubID.choices = [(row.PubID, row.PubID) for row in Publication.query.with_entities(Publication.PubID)]

        #retrieve author IDs
        self.AuthorID.choices = [(row.AuthorID, row.FirstName + ' ' + row.LastName) 
                                for row in Author.query.with_entities(Author.AuthorID, Author.FirstName, Author.LastName)]

class AssignForm(AssignUpdateForm):

    submit = SubmitField('Submit Assignment')