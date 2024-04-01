# FYP 0552-Natural Language Processing for automatically creating radiological reports

#### This repository contains two main folders, the `ct-segmentor` and `radmix-development` folders that are used in the development of RadMix, a LLM aimed at generating radiological findings with volumetric data when given a patient's medical condition.

### Radmix-development
This `radmix-development` folder contains files associated to data preprocessing, pretraining and evaluation of the LLM that is being created.

During the data proprocessing portion, MIMIC-III dataset and oasis dataset are being used in the process.
Files associated with data preprocessing includes:
- `cleanData.ipynb`: This file contains code to cleaning and adding volumetric data to created the `updated_clean_data_values.json` which will then be used to form the train and test set.
- `combineElderlyData.ipynb`: This file contains code that is used to create a csv that can be is being used to obtained the `combined_oasis.csv` file.
- `combined_oasis.csv`: This file contains patient details from oasis dataset that was given, ranging from teenagers to elderlies, which is then used in the `cleanData.ipynb` file alongside MIMIC-III dataset.
- `creationOfCombinedCsv.ipynb`: This file is used to concatenate the various csv to obtain the `combined_oasis.csv` file.

All the file above constituted to the creating of the training and testing set that will then be used in pretraininig. `pretraining.ipynb` contains the code regarding the PEFT fine-tuning method that was adopted to obtain our final model RadMix. There consist of a folder `mixtral-Radmix-checkpoint-300` in the folder as well, however, due the file limt size in github, certain files such as adapters.safetensors are not present. To view the model do check out this path in bionet `data/herm0011/mixtral-Radmix` to view different checkpoint models as well. The model that have the lowest lost was used in our case, which is the model at checkpoint 300.

After obtaining the RadMix model, evaluation was conducted on RadMix and the base model Mixtral, files associated to it are `evaluation.ipynb` and `evalbaseModel.ipynb` respectively.


### CT-segmentor

This folder contains files that should be changed in the main repository, to integrate RadMix into the toolkit. To view the integration, do follow the path in bionet `home/herm/ct-segmentor` to view the changes and run the toolkit locally as well.

Commands to run the toolkit:
```bash
#To run the frontend
$ npm install
$ npm run start
```
```bash
#To run the backend
$ flask run --port=5004
```

The files in the `Backend` folder are associated to creating an endpoint as well as instantiating the RadMix model when the backend is up and running. On the other hand, the file in the `Frontend` folder contains the function `handleGenerateFindings` and new htmls tags from line 353-367 that will allow the endpoint to be called from the Frontend to present the generated findings in the toolkit.
