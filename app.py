from fastapi import FastAPI
from fastapi.responses import JSONResponse
import pandas as pd
from typing import Annotated, Literal
import pickle
from pydantic import BaseModel, Field, computed_field

with open("model.pkl","rb") as f:
    model=pickle.load(f)

app=FastAPI()

tier_1_cities=["delhi","mumbai","banglore","pune","chennai","hyderabad"]
tier_2_cities=[
    "nagpur","thane","jaipur","lakhnow","indore","patana","ranchi","belgum",
    "vishakhapattnam","chandigarh","udaipur","aurangabad","hubbli","nashik",
    "bhavnagar","gunttur","mangloare","surat","satara","kolahpur","warangal",
    "gwalior","vizag","maysore","jabalpur","dehradhun","tiruvanantpuram","guhavati"
]

class UserInput(BaseModel):
    age:Annotated[int, Field(...,gt=0,lt=120, description="age of the user")]
    weight:Annotated[float, Field(...,gt=0, description="weight of the user")]
    height:Annotated[float, Field(...,gt=0,lt=2.5, description="height of the user")]
    income_lpa:Annotated[int, Field(...,gt=0,lt=120, description="annual salary of of the user")]
    smoker:Annotated[bool, Field(..., description="is user a smoker")]
    city:Annotated[str, Field(..., description="city that user belongs to")]
    occupation:Annotated[Literal['retired', 'freelancer', 'student', 'government_job',
       'business_owner', 'unemployed', 'private_job'],Field(...,description="occupation of the user")]

    @computed_field
    @property
    def bmi(self)->float:
        return self.weight/(self.height**2)

    @computed_field
    @property
    def age_group(self)->str:
        if self.age < 25:
            return "young"
        elif self.age < 45:
            return "adult"
        elif self.age < 60:
            return "middle aged"
        else:
            return "senior"

    @computed_field
    @property
    def lifestyle_risk(self)->str:
        if self.smoker==True and self.bmi > 30:
            return "high"
        elif self.smoker==True and self.bmi>27:
            return "medium"
        else:
            return "low"

    @computed_field
    @property
    def city_tier(self)->int:
        if self.city in tier_1_cities:
            return 1
        elif self.city in tier_2_cities:
            return 2
        else:
            return 3

@app.get("/")
def home():
    return {"Message":"hello"}

@app.post("/predict")
def predictpremium(data:UserInput):
    input_df=pd.DataFrame([{
        'bmi':data.bmi,
        'age_group':data.age_group,
        'lifestyle_risk':data.lifestyle_risk,
        'city_tier':data.city_tier,
        'income_lpa':data.income_lpa,
        'occupation':data.occupation
    }])

    prediction=model.predict(input_df)[0]

    return JSONResponse(status_code=200,content={'predicted_category':prediction})