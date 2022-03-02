from flask import Flask
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, RadioField, DecimalField, SelectField, IntegerField
from wtforms.validators import DataRequired, ValidationError
from wtforms.validators import NumberRange, InputRequired
from flask_admin.form import DateTimePickerWidget
from wtforms.fields.html5 import DateField
from datetime import date

class EntryForm(FlaskForm):
  host_since=DateField('Host Since')
  host_response_rate=DecimalField("Host Response Rate", validators=[InputRequired('Field is required'), NumberRange(min=0, max=100, message='Please enter a number between 0 and 100')])
  host_listings_count=IntegerField("Host Listings Count", validators=[InputRequired('Field is required'), NumberRange(min=0, message="Please enter an integer greater or equal to 0")])
  latitude=DecimalField("Latitude", validators=[InputRequired('Field is required')])
  longitude=DecimalField("Longitude", validators=[InputRequired('Field is required')])
  accommodates=IntegerField("Accommodates", validators=[InputRequired('Field is required'), NumberRange(min=1, message="Please enter an integer greater or equal to 1")])
  bedrooms=IntegerField("Bedrooms", validators=[InputRequired('Field is required'), NumberRange(min=1, message="Please enter an integer greater or equal to 1")])
  price=DecimalField("Price", validators=[InputRequired('Field is required'), NumberRange(min=0, message="Please enter a number greater or equal to 0")])
  minimum_nights=IntegerField("Minimum Nights", validators=[InputRequired('Field is required'), NumberRange(min=1, message="Please enter an integer greater or equal to 1")])
  maximum_nights=IntegerField("Maximum Nights", validators=[InputRequired('Field is required'), NumberRange(min=1, message="Please enter an integer greater or equal to 1")])
  availability_30=IntegerField("Availability 30", validators=[InputRequired('Field is required'), NumberRange(min=0, max=30, message="Please enter an integer between 0 and 30")])
  number_of_reviews=IntegerField("Number of Reviews", validators=[InputRequired('Field is required'), NumberRange(min=0, message="Please enter an integer greater or equal to 0")])
  host_response_time=SelectField("Host Response Time", choices=[("within an hour", "within an hour"), ("within a few hours", "within a few hours"), ("within a day", "within a day"),
  ("a few days or more", "a few days or more")], validators=[DataRequired()])
  host_is_superhost=SelectField("Host is Superhost", choices=[("Yes", "Yes"), ("No", "No")], validators=[DataRequired()])
  host_identity_verified=SelectField("Host's Identity is Verified", choices=[("Yes", "Yes"), ("No", "No")], validators=[DataRequired()])
  room_type=SelectField("Room Type", choices=[("Entire home/apt", "Entire home/apt"), ("Hotel room", "Hotel room"), ("Private room", "Private room"),
  ("Shared room", "Shared room")], validators=[DataRequired()])
  instant_bookable=SelectField("Instant Bookable", choices=[("Yes", "Yes"), ("No", "No")], validators=[DataRequired()])
  submit=SubmitField("Submit and Proceed to Model 2")

  def validate_host_since(self, fill):
    if fill.data is not None and fill.data > date.today():
      raise ValidationError('Host Since Date cannot be a future date.')
  
  def validate_maximum_nights(self, fill):
    if fill.data is not None and self.minimum_nights.data is not None and fill.data < self.minimum_nights.data:
      raise ValidationError('Maximum Nights cannot be smaller than Minimum Nights.')

class TextForm(FlaskForm):
  comment =  StringField("Comment", validators=[DataRequired()])
  submit_comment = SubmitField("Submit and Go to Summary")

class CancelForm(FlaskForm):
  cancel=SubmitField("Clear and Restart")
  
