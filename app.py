from flask import Flask, render_template, request, redirect, url_for, session
import jinja2
from jinja2 import Template
from map import map_init
from forms import EntryForm, TextForm, CancelForm
import tensorflow as tf
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
import pickle
import numpy as np
import pandas as pd
from datetime import date
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'SECRET_PROJECT'

main_tabs={"model_specification": "Model 1: Prediction of Review Score", "room_review": "Model 2: Sentiment Classification", "summary": "Summary"}

index_score=pd.Index(['host_since_days', 'host_response_rate', 'host_listings_count',
       'latitude', 'longitude', 'accommodates', 'bedrooms', 'price',
       'minimum_nights', 'maximum_nights', 'availability_30',
       'number_of_reviews', 'host_response_time_within a day',
       'host_response_time_within a few hours',
       'host_response_time_within an hour', 'host_is_superhost_t',
       'host_identity_verified_t', 'room_type_Hotel room',
       'room_type_Private room', 'room_type_Shared room',
       'instant_bookable_t'],
      dtype='object')

with open("ridge_model.pkl", "rb") as file:
    model=pickle.load(file)

tf_model=tf.keras.models.load_model("tf_model.h5")
with open("tokenizer.pickle", "rb") as handle:
    tokenizer=pickle.load(handle)

@app.route("/")
def home():
    return render_template("about.html", main_tabs=main_tabs )

@app.route('/map')
def map():
   map=map_init()
   return map._repr_html_()

@app.route('/model_specification', methods=["GET", "POST"])
def tabs():
    form=EntryForm(csrf_enabled=False)
    if request.method== 'POST':
        if form.validate_on_submit():
            session['host_since']=form.host_since.data
            session['host_since_days']=int((pd.to_datetime(date.today())-pd.to_datetime(session['host_since']))/np.timedelta64(1,"D"))
            session['host_response_rate']=float(form.host_response_rate.data)
            session['host_listings_count']=int(form.host_listings_count.data)
            session['latitude']=float(form.latitude.data)
            session['longitude']=float(form.longitude.data)
            session['accommodates']=int(form.accommodates.data)
            session['bedrooms']=int(form.bedrooms.data)
            session['price']=float(form.price.data)
            session['minimum_nights']=int(form.minimum_nights.data)
            session['maximum_nights']=int(form.maximum_nights.data)
            session['availability_30']=int(form.availability_30.data)
            session['number_of_reviews']=int(form.number_of_reviews.data)
            session['host_response_time']=form.host_response_time.data
            session['host_is_superhost']=form.host_is_superhost.data
            session['host_identity_verified']=form.host_identity_verified.data
            session['room_type']=form.room_type.data
            session['instant_bookable']=form.instant_bookable.data

            session['score_data']=pd.DataFrame().append({"host_since_days":session['host_since_days'], "host_response_rate":session["host_response_rate"]/100,  
            "host_listings_count":session["host_listings_count"], "latitude":session["latitude"], "longitude":session["longitude"], "accommodates":session["accommodates"],
            "bedrooms":session["bedrooms"], "price":session["price"], "minimum_nights":session["minimum_nights"], "maximum_nights":session["maximum_nights"],
             "availability_30":session["availability_30"], "number_of_reviews":session["number_of_reviews"], "host_response_time_within a day": 1 if session["host_response_time"]=="within a day" else 0,
             "host_response_time_within a few hours": 1 if session["host_response_time"]=="within a few hours" else 0,
             "host_response_time_within an hour": 1 if session["host_response_time"]=="within an hour" else 0, 
              "host_is_superhost_t": 1 if session["host_is_superhost"]=="Yes" else 0,  "host_identity_verified_t": 1 if session["host_identity_verified"]=="Yes" else 0,
              "room_type_Hotel room": 1 if session["room_type"]=="Hotel room" else 0, "room_type_Private room": 1 if session["room_type"]=="Private room" else 0,
              "room_type_Shared room": 1 if session["room_type"]=="Shared room" else 0, "instant_bookable_t": 1 if session["instant_bookable"]=="Yes" else 0}, ignore_index=True).to_dict('list')

            session['predictions_1']=model.predict(pd.DataFrame(session['score_data'])[index_score].iloc[0:1])[0]
            session['predictions_1']=np.round(session['predictions_1'], 2)
            if session['predictions_1']>5:
                session['predictions_1']=5
            if session['predictions_1']<0:
                session['predictions_1']=0
            return redirect(url_for('review'))
    return render_template("tabs.html", main_tabs=main_tabs, template_form=form)


@app.route('/room_review', methods=["GET", "POST"])
def review():
    text_form=TextForm(csrf_enabled=False)
    if request.method== 'POST':
        if text_form.validate_on_submit():
            session['reviews']=text_form.comment.data
            newword=tokenizer.texts_to_sequences([session['reviews'].lower()])
            max_length=120
            padding_type='post'
            trunc_type='post'
            newword = pad_sequences(newword, maxlen=max_length, padding=padding_type, truncating=trunc_type)
            newword = np.array(newword)
            session['predictions_2']=tf_model.predict(newword)[0][0]
            session['predictions_2']="favorable" if session['predictions_2']>=0.5 else "unfavorable"

            return redirect(url_for('summary', main_tabs=main_tabs))
    return render_template("review.html", main_tabs=main_tabs, template_form=text_form)

@app.route('/summary', methods=["GET", "POST"])
def summary():
    cancel_form=CancelForm(csrf_enabled=False)
    if request.method== 'POST':
        if cancel_form.validate_on_submit():
            session.clear()
            return redirect(url_for('about'))
    return render_template("summary.html", main_tabs=main_tabs, cancel_form=cancel_form)



@app.route("/about")
def about():
    return render_template("about.html", main_tabs=main_tabs)

if __name__ == '__main__':
    app.run()

