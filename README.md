[![Build Status](https://travis-ci.com/watakandhi/gunosy_coding_task.svg?token=UPeNZfpEiF2sCZduAo4d&branch=master)](https://travis-ci.com/watakandhi/gunosy_coding_task)

# To get the image
<img src="images/home_view.png" width="300">   
<img src="images/transition_view.png" width="500">   
<img src="images/transition_view2.png" width="300">   

# Tutorial
To launch the website  
```
docker-compose build 
docker-compose up
```
`Ctl+c` to stop running the server. 

To collect data from a website  
```
docker-compose run webapp python manage.py collect_data
```

To train the model
```
docker-compose run webapp python manage.py train 
```
This will output the accuracy of a classifier using the test dataset
Now run `docker-compose up` again to launch the website


# Accuracy
Accuracy: Naive Bayes ... 0.74167
Accuracy: Random Forest ... 0.82083