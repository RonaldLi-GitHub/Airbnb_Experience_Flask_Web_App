from flask import Flask, render_template, request, redirect, url_for
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


main_tabs={"model_specification": "Model 1: Prediction of Review Score", "room_review": "Model 2: Sentiment Classification", "summary": "Summary"}
host_since={}
host_since_days={}
host_response_rate={}
host_listings_count={}
latitude={}
longitude={}
accommodates={}
bedrooms={}
price={}
minimum_nights={}
maximum_nights={}
availability_30={}
number_of_reviews={}
host_response_time={}
host_is_superhost={}
host_identity_verified={}
room_type={}
instant_bookable={}
reviews={}
predictions_1={}
predictions_2={}
score_X={}
score_X_transformed={}
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
            id=len(host_since_days)+1
            with open("ridge_model.pkl", "rb") as file:
                model=pickle.load(file)
            host_since[id]=form.host_since.data
            host_since_days[id]=(pd.to_datetime(date.today())-pd.to_datetime(host_since[id]))/np.timedelta64(1,"D")
            host_response_rate[id]=form.host_response_rate.data/100
            host_listings_count[id]=form.host_listings_count.data
            latitude[id]=form.latitude.data
            longitude[id]=form.longitude.data
            accommodates[id]=form.accommodates.data
            bedrooms[id]=form.bedrooms.data
            price[id]=form.price.data
            minimum_nights[id]=form.minimum_nights.data
            maximum_nights[id]=form.maximum_nights.data
            availability_30[id]=form.availability_30.data
            number_of_reviews[id]=form.number_of_reviews.data
            host_response_time[id]=form.host_response_time.data
            host_is_superhost[id]=form.host_is_superhost.data
            host_identity_verified[id]=form.host_identity_verified.data
            room_type[id]=form.room_type.data
            instant_bookable[id]=form.instant_bookable.data
            score_X[id]={"host_since": host_since[id], "host_since_days":host_since_days[id], "host_response_rate": host_response_rate[id], "host_listings_count":host_listings_count[id], 
            "latitude": latitude[id], "longitude": longitude[id], "accommodates": accommodates[id], "bedrooms":bedrooms[id], "price": price[id], 
            "minimum_nights": minimum_nights[id], "maximum_nights": maximum_nights[id],  "availability_30": availability_30[id], "number_of_reviews": number_of_reviews[id],
            "host_response_time": host_response_time[id], "host_is_superhost":host_is_superhost[id], "host_identity_verified": host_identity_verified[id], 
            "room_type": room_type[id], "instant_bookable": instant_bookable[id]}
            score_X_transformed[id]=pd.DataFrame().append({"host_since_days":score_X[id]["host_since_days"], "host_response_rate":score_X[id]["host_response_rate"],  
            "host_listings_count":score_X[id]["host_listings_count"], "latitude":score_X[id]["latitude"], "longitude":score_X[id]["longitude"], "accommodates":score_X[id]["accommodates"],
            "bedrooms":score_X[id]["bedrooms"], "price":score_X[id]["price"], "minimum_nights":score_X[id]["minimum_nights"], "maximum_nights":score_X[id]["maximum_nights"],
             "availability_30":score_X[id]["availability_30"], "number_of_reviews":score_X[id]["number_of_reviews"], "host_response_time_within a day": 1 if score_X[id]["host_response_time"]=="within a day" else 0,
             "host_response_time_within a few hours": 1 if score_X[id]["host_response_time"]=="within a few hours" else 0,
             "host_response_time_within an hour": 1 if score_X[id]["host_response_time"]=="within an hour" else 0, 
              "host_is_superhost_t": 1 if score_X[id]["host_is_superhost"]=="Yes" else 0,  "host_identity_verified_t": 1 if score_X[id]["host_identity_verified"]=="Yes" else 0,
              "room_type_Hotel room": 1 if score_X[id]["room_type"]=="Hotel room" else 0, "room_type_Private room": 1 if score_X[id]["room_type"]=="Private room" else 0,
              "room_type_Shared room": 1 if score_X[id]["room_type"]=="Shared room" else 0, "instant_bookable_t": 1 if score_X[id]["instant_bookable"]=="Yes" else 0}, ignore_index=True)

            score_X_transformed[id]=score_X_transformed[id][index_score]

            predictions_1[id]=model.predict(score_X_transformed[id].iloc[0:1])[0]
            if predictions_1[id]>5:
                predictions_1[id]=5
            if predictions_1[id]<0:
                predictions_1[id]=0
            predictions_1[id]=float(np.round(predictions_1[id], decimals=2))
            '''return redirect(url_for('summary', main_tabs=main_tabs, entry=reviews, last_id_1=len(score_X), last_id_2=len(reviews),predictions_1=predictions_1,
             predictions_2=predictions_2,
            score_X_transformed=score_X_transformed, score_X=score_X))'''
            return redirect(url_for('review'))
    return render_template("tabs.html", main_tabs=main_tabs, template_form=form)


@app.route('/room_review', methods=["GET", "POST"])
def review():
    text_form=TextForm(csrf_enabled=False)
    if request.method== 'POST':
        if text_form.validate_on_submit():
            id=len(reviews)+1
            reviews[id]=text_form.comment.data
            model=tf.keras.models.load_model("tf_model.h5")
            with open("tokenizer.pickle", "rb") as handle:
                tokenizer=pickle.load(handle)
            newword=tokenizer.texts_to_sequences([text_form.comment.data.lower()])
            max_length=120
            padding_type='post'
            trunc_type='post'
            newword = pad_sequences(newword, maxlen=max_length, padding=padding_type, truncating=trunc_type)
            newword = np.array(newword)
            predictions_2[id]=model.predict(newword)[0][0]
            predictions_2[id]="favorable" if predictions_2[id]>=0.5 else "unfavorable"

            return redirect(url_for('summary', main_tabs=main_tabs, entry=reviews, last_id_1=len(score_X), last_id_2=len(reviews), predictions_1=predictions_1,
            predictions_2=predictions_2,
            score_X_transformed=score_X_transformed, score_X=score_X))


    return render_template("review.html", main_tabs=main_tabs, template_form=text_form)

@app.route('/summary', methods=["GET", "POST"])
def summary():
    cancel_form=CancelForm(csrf_enabled=False)
    if request.method== 'POST':
        if cancel_form.validate_on_submit():
            host_since.clear()
            host_since_days.clear()
            host_response_rate.clear()
            host_listings_count.clear()
            latitude.clear()
            longitude.clear()
            accommodates.clear()
            bedrooms.clear()
            price.clear()
            minimum_nights.clear()
            maximum_nights.clear()
            availability_30.clear()
            number_of_reviews.clear()
            host_response_time.clear()
            host_is_superhost.clear()
            host_identity_verified.clear()
            room_type.clear()
            instant_bookable.clear()
            reviews.clear()
            predictions_1.clear()
            predictions_2.clear()
            score_X.clear()
            score_X_transformed.clear()
            
            return redirect(url_for('about'))
    return render_template("summary.html", main_tabs=main_tabs, entry=reviews, last_id_1=len(score_X), last_id_2=len(reviews), predictions_1=predictions_1,
    predictions_2=predictions_2, score_X_transformed=score_X_transformed, score_X=score_X, cancel_form=cancel_form)



@app.route("/about")
def about():
  return render_template("about.html", main_tabs=main_tabs)

if __name__ == '__main__':
   port = int(os.environ.get("PORT", 5000))
   app.run(debug=True, port=port)

