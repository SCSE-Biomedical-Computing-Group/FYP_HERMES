import os
from pathlib import Path
import ast
import yaml
from PIL import Image
import json
import flask
import sqlalchemy
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import yaml
import numpy as np
import pandas as pd
import datetime
from src.fetch import *
from src.model import *

from src.utils import  CT_Pipeline, CACHE, SERVER_IP, Manager, get_current_port, Annotater, ReportManager
from src.report import report_vis


import seaborn as sns
import matplotlib.pyplot as plt

import logging
logging.getLogger('flask_cors').level = logging.DEBUG

####################################################

def db_connect():
    #user = input("AWS RDS Username:")
    #pwd = getpass.getpass('Password:')
    user = 'toolkit'
    pwd = 'radi8tion'
    return f'postgresql://{user}:{pwd}@ec2-13-250-219-240.ap-southeast-1.compute.amazonaws.com:5432/database-1' 

## Declaring global vars

app = Flask(__name__)
app.url_map.strict_slashes = False
CORS(app)

#app.config['SQLALCHEMY_DATABASE_URI'] = db_connect()
#db = SQLAlchemy(app)
#engine = sqlalchemy.create_engine(db_connect())



TARGET_DIR = CACHE
TARGET_DIR_TISSUE = TARGET_DIR + 'tissue/'
TARGET_DIR_BASELINE = TARGET_DIR + 'baseline/'

for project in ['ich', 'tissue']:
    os.makedirs(Path(TARGET_DIR)/project, exist_ok=True)


# Config file for projects
with open(Path(__file__).parent / "src/backend_model.yaml", 'r') as f:
    valuesYaml = yaml.load(f, Loader=yaml.FullLoader)


fetcher = Fetcher(Path(__file__).parent / 'src/credentials.yaml')
assert callable(fetcher.fetch_fn), f'Wrong ID and Password. {fetcher.fetch_fn}'

####################################################




reporter = ReportManager()
reporter_tissueseg = ReportManager('tissueseg')


def age_band(age):
    if age >= 22 and age <= 25:
        return '22-25'
    elif age >= 26 and age <= 30:
        return '26-30'
    elif age >= 31 and age <= 35:
        return '31-35'
    else: # will put <22 here too... 
        return '36+'

def generate_plot(args ):
    
    series = args.get('series')
    # if task == 'bet':
    #     task = 'ticv'

    data = reporter_tissueseg.load_volume(series)
    # print(type(data), data)
    vol = data['Volume']['Total'] #/1000
    classes = {
              'ticv' : ['bet'],
              'tbv' : ['gm','wm'],
              'vent' : ['vent'],
            }

    fig, ax = plt.subplots(1, len(classes), figsize=(20,5))


    hcp_path = CACHE+'/vol_hcp.csv'
    kcl_path = CACHE+'/vol_kcl.csv'
    aomic_path = CACHE+'/vol_aomic.csv'
    
    hcp = pd.read_csv(hcp_path)
    #kcl = pd.read_csv(kcl_path)
    #aomic = pd.read_csv(aomic_path)
    
    hcp.rename(columns={'Subject': 'sub_id', 'Age': 'age', 'Gender': 'gender'}, inplace=True)
    hcp['sub_id'] = 'HCP_' + hcp['sub_id'].astype('str')
    
    hcp_grouped = hcp.groupby(['age']).describe()
    #import pdb; pdb.set_trace()

    dcmfile, pseudo_name = fetcher(args)

    for i, c in enumerate(classes):
        query = sum(list(map( lambda x: vol[x], classes[c] )))
        age_raw = dcmfile[0][('0010','1010')] # series so just get from first dcm, 022Y
        age = int(age_raw[:-1])
        age_range = age_band(age)
        sns.lineplot(data=hcp_grouped[c][['25%', '50%', '75%']], ax=ax[i])
        ax[i].plot(age_range, query, 'rp') # https://stackoverflow.com/a/46637880
        ax[i].set_title(c.upper())
    
    
    # need to get vol and age range
    
    
    
    
    plt.savefig(Path(TARGET_DIR)/ 'tissueseg' / f'distplot_{series}.png')
    plt.close()


#def generate_plot(args):
#    
#    series = args.get('series')
#    task = args.get('task')
#    # if task == 'bet':
#    #     task = 'ticv'
#
#    hcp_path = '/home/data_repo/cache/vol_hcp.csv'
#    # kcl_path = '/home/data_repo/cache/vol_kcl.csv'
#    # aomic_path = '/home/data_repo/cache/vol_aomic.csv'
#    
#    hcp = pd.read_csv(hcp_path)
#    # kcl = pd.read_csv(kcl_path)
#    # aomic = pd.read_csv(aomic_path)
#    
#    hcp.rename(columns={'Subject': 'sub_id', 'Age': 'age', 'Gender': 'gender', 'ticv': 'bet'}, inplace=True)
#    hcp['sub_id'] = 'HCP_' + hcp['sub_id'].astype('str')
#    
##     hcp.loc[hcp['age'] == '26-30','age'] = hcp['age'].apply(lambda x: np.random.choice(list(range(26,31)),1)[0])
##     hcp.loc[hcp['age'] == '31-35','age'] = hcp['age'].apply(lambda x: np.random.choice(list(range(31,36)),1)[0])
##     hcp.loc[hcp['age'] == '22-25','age'] = hcp['age'].apply(lambda x: np.random.choice(list(range(22,26)),1)[0])
##     hcp['age'].replace('36+', 36, inplace=True)
#    
##     kcl.drop(['weight', 'size', 'injected_dose', 'activity_in_ICV_mask', 'handedness', 'birth_date'], axis=1, inplace=True)
##     kcl.rename(columns={'participant_id': 'sub_id', 'sex': 'gender'}, inplace=True)
##     kcl['sub_id'] = 'KCL_' + kcl['sub_id'].astype('str')
#    
##     aomic.rename(columns={'participant_id': 'sub_id', 'Age': 'age', 'Gender': 'gender'}, inplace=True)
##     aomic['sub_id'] = 'AOMIC_' + aomic['sub_id'].astype('str')
#    
##     combined = pd.concat([hcp, kcl, aomic])
#    
#    hcp_grouped = hcp.groupby(['age']).describe()
#    sns.lineplot(data=hcp_grouped[task][['25%', '50%', '75%']])
#    
#    
#    # need to get vol and age range
#    dcmfile, pseudo_name = fetcher(args)
#    age_raw = dcmfile[0][('0010','1010')] # series so just get from first dcm, 022Y
#    age = int(age_raw[:-1])
#    age_range = age_band(age)
#    
#    
#    data = reporter_tissueseg.load_volume(series)
#    # print(type(data), data)
#    vol = data['Volume']['Total'][task] #/1000
#    
#    
#    plt.plot(age_range, vol, 'rp') # https://stackoverflow.com/a/46637880
#    plt.savefig(Path(TARGET_DIR)/ 'tissueseg' / f'plot_{series}_{task}.png')
#    plt.close()

def retrieve_preproc_data(args):
    
    dcmfile, pseudo_name = fetcher(args)
    if ('wl' in args) & ('ww' in args):
        ww = args.get('ww')
        wl = args.get('wl')
        ww = int(ww) if ww is not None else ww
        wl = int(wl) if wl is not None else wl
    else:
        ww = 80
        wl = 40
    
    with CT_Pipeline(ww=ww,wl=wl) as ct_pipe:
        dcmfile = ct_pipe(dcmfile)
    for obj, val in zip(dcmfile, pseudo_name['instanceID']):
        obj.attr('orthancID', val)
        obj.attr('orthancSeriesID', pseudo_name['seriesID'])
        
    return (dcmfile, pseudo_name)


def baseline(args):
    
    frontend_json = {}
    
    (dcmfile, pseudo_name) = retrieve_preproc_data(args)
    
    unet.model(dcmfile, args)
    
    

def seg_tissue(args,init=False , model='baseline'):
    # # TODO: return json
    # dcmfile, pseudo_name = fetcher(args) # frontend url args
    # # TODO: ww/wl
    # with CT_Pipeline() as ct_pipe:
    #     dcmfile = ct_pipe(dcmfile)
    # # TODO: standardise database lookup
    
    #(dcmfile, pseudo_name) = retrieve_preproc_data(args)

    if init is None: init = False
    with Manager(args=args, fetcher=fetcher,project='tissueseg' , modality='CT', lookup= not init ,save_preprocess=True, parallel=False) as mgr:
        if mgr.dcmfile is not None:
            if model == 'baseline':
                #frontend_json = mgr.postprocess(unet.model(dcmfile, args))
                #out = dict( [ (k ,m(mgr.dcmfile, args) ) for k,m in unet.models.items()]) # {'class' : {inst1: ,... } }
                out = dict( [ (k ,m(mgr.dcmfile) ) for k,m in unet.models.items()]) # {'class' : {inst1: ,... } }
                frontend_json = mgr.postprocess(out)
            else:
                frontend_json = mgr.postprocess(p2p.model(mgr.dcmfile, args))

        else:
            frontend_json = mgr.frontend_json


    return frontend_json


def detectICH(args, init=False):

    '''
    Getting segmentation mask png path and change its name to orthanc server ID.

    dcmfile : List of Dicom objects (1 for slice)
    complete_mask : Dict [UID : mask png path]
    get_json : Dict [UID : [Subtype :[bbox, maskpng] ] ]

    '''
    if init is None: init = False
    with Manager(args=args, fetcher=fetcher, project='ICH' , modality='CT', lookup= not init ,save_preprocess=True, parallel=False) as mgr:
        
        if mgr.dcmfile is not None:
            #get_json, complete_mask = to_json(*ich_model.model(data=inp.dcmfile))
            get_json, complete_mask = mgr.postprocess(*ich_model.model(data=mgr.dcmfile))
            frontend_json = complete_mask
 
        else:
            frontend_json = mgr.frontend_json
    return frontend_json



@app.route('/sample', methods=['GET'])
def return_sample_mask():
    '''
    Returns a sample mask png from the cache
    #TODO: remove when no longer needed
    '''

    args = request.args

    try:
        instance_id = args.get('instance')
    except AttributeError:
        instance_id = None

    if instance_id is not None:
        mask = '/data/data_repo/neuro_img/anat_brain_img/cache/ich/' + instance_id + '.png'
    else:
        mask = '/data/data_repo/neuro_img/anat_brain_img/cache/ich/mask.png'

    # this will overwrite all
    mask = '/home/data_repo/cache/empty.png'

    return send_file(mask, mimetype='image/png')


@app.route('/inference/ich/', methods=['GET'])
def inference_ich():
    '''
    instance: str, specify instance ID
    series : str, specify series ID 
    inter: str, set as 'yes' to get intermediate preprocessing image
    wl: int, to set the pipeline config for window level
    ww: int, to set the pipeline config for window width

    If ww and wl not specified, will default to 80,40. To use dicom original value for ww/wl, specify None,None
    '''
    try:
        args = request.args
        init = args.get('init')
        get_json = detectICH(args, init)

        #if args.get('inter') == 'yes':
        #    return send_file(str(Path(TARGET_DIR)) + '/ICH/' + list(get_json.values())[0].split('=')[-1]+ '_inter.png', mimetype='image/png')

        return get_json

    except AttributeError as e:
        raise e
        resp = jsonify(message="No ids provided.", category="error", status=404)
        return resp




@app.route('/inference/tissue/', methods=['GET'])
def inference_tissue():
    '''
    Query must specify instance and task (which kind of seg: wm, gm, csf, vent, bet)
    Currently returns PNG. should make it return json
    '''

    try:

        args = request.args # these args are from frontend, in the url

        init = args.get('init')
        get_json = seg_tissue(args, init, model='baseline') # this will save the files into TARGET_DIR_TISSUE

        return get_json

    except AttributeError as e:

        print('\nHere is the error:')
        print(e)

        resp = jsonify(message="No ids provided.", category="error", status=404)
        return resp




@app.route('/annotation/<proj>/<task>', methods=['POST'])
def update_ich_mask(proj, task):
    mask_annotater = Annotater(project=proj,task='mask')
    box_annotater = Annotater(project=proj,task='box')
    if request.method == 'POST':
        try:
            update = request.get_json()
            user = request.args.get('user')
            series_id = request.args.get('series')
            mask_annotater(user,series_id, update )
            box_annotater(user,series_id, update )
            return jsonify(success=True)
        except Exception as e:
            print(e)
            resp = jsonify(message="Only JSON is allowed. Please check on the arguments.", category="error", status=404)
            return resp

    resp = jsonify(message="Only POST request.", category="error", status=404)
    return resp
        





@app.route('/retrieve/<proj>/', methods=['GET'])
def retrieve(proj):
    try:
        args = request.args
        instance = args.get('instance')
               

        if proj.lower() == 'ich':
            mask = Path(TARGET_DIR)/'ich/' / f'{instance}_bb.png'
        elif proj.lower() in ['tissue', 'tissueseg']:
            task = args.get('task').lower()
            #assert task in [ 'wm', 'gm', 'csf', 'vent', 'bet']
            assert task in unet.tissue_classes , f'`task` must be one of {unet.tissue_classes}'
            mask = Path(TARGET_DIR)/ 'tissueseg' / f'{instance}_{task}.png'
            #mask = TARGET_DIR_TISSUE + args.get('task') + '/' + instance + '.png'

        return send_file(mask, mimetype='image/png')

    except (AttributeError, AssertionError) as e:
        raise e
        resp = jsonify(message=e, category="error", status=404)
        return resp





@app.route('/retrieve_np/<proj>/', methods=['GET'])
def retrieve_np(proj):
    try:
        args = request.args
        id = args.get('series') #from instance to series
        original = args.get('original')
        if original is None: original = False

        if proj.lower() == 'ich':
            np_path = Path(TARGET_DIR)/'ich/' / f'{id}.npy'
            edited_np_path = Path(TARGET_DIR)/'ich/' / f'{id}edit.npy' #only store last edit

            if os.path.exists(edited_np_path) & (not original):
                np_path = edited_np_path
            


        elif proj.lower() in ['tissueseg','tissue'] :
            task = args.get('task').lower()
            assert task in [ 'wm', 'gm', 'csf', 'vent', 'bet']
            np_path = Path(TARGET_DIR)/ 'tissueseg'  / f'{id}_{task}.npy'
        return send_file(np_path)

    except AttributeError as e:
        resp = jsonify(message="No ids provided or check arguments.", category="error", status=404)
        return resp








@app.route('/report/<version>/<project>/', methods=['GET', 'POST'])
def report(version, project):
    args = request.args
    series = args.get('series')
    


    if version.lower() == 'summary':
       if request.method == 'GET':
            if project == 'ich':
                data = reporter.load_volume(series)
            elif project in ['tissue','tissueseg']:
                data = reporter_tissueseg.load_volume(series)
            else:
                raise NotImplementedError 



    elif version.lower() == 'detail':
       user = int(args.get('user')) #only allow integer user
       series = args.get('series')
       if request.method == 'GET':
            if 'template' in args: template = args.get('template') 
            else: template = False
            data = reporter.load_text_report(series, user, template)

       if request.method == 'POST':
            try:
                data = request.get_json() #not using FORMDAT
                reporter.update_text_report(series, user, data)

                
            #except (AttributeError, AssertionError) as e:
            except Exception  as e:
                print(e)
                resp = jsonify(message="No json received", category="error", status=404)
                return resp
            return jsonify(success=True)

    else: pass

    return jsonify(data)





@app.route('/preprocess', methods=['GET'])
def load_dcm():
    try:
        args = request.args
        instance_id = args.get('instance')
        
        path = Path(TARGET_DIR)/'ich' / f'{instance_id}_inter.png'
        assert os.path.isfile(path)
        return send_file(path, mimetype='image/png')
    
    except (AttributeError, AssertionError) as e:
        resp = jsonify(message="No instance id provided or Data does not exist", category="error", status=404)
        return resp


@app.route('/report_im/<project>/', methods=['GET'])
def report_img(project):
    msg = "No instance id provided or Data does not exist"
    try:
        args = request.args
        instance_id = args.get('instance')
        im_path = Path(TARGET_DIR)/'ich' / f'{instance_id}_inter.png'
        
        if project.lower() == 'ich':
            msk_path = Path(TARGET_DIR)/'ich' / f'{instance_id}.npy'

        elif project.lower() in ['tissue', 'tissueseg']:
            if args.get('task') is None: 
                msg = 'Task argument is not specified.'
                raise AssertionError
            task = args.get('task')
            im_path = Path(TARGET_DIR)/'tissueseg' / f'{instance_id}_inter.png'
            msk_path = Path(TARGET_DIR)/'tissueseg' / f'{instance_id}_{task}.npy'

       
        report_im_path = report_vis(im_path, msk_path)

        return send_file(report_im_path, mimetype='image/png')
    
    except (AttributeError, AssertionError) as e:
        resp = jsonify(message = msg, category="error", status=404)
        return resp


@app.route('/bbox_png', methods=['GET'])
def get_bbox_im():
    try:
        args = request.args
        id = args.get('instance')
        im_path = Path(TARGET_DIR)/'ich' / f'{id}_bb.png'
        #msk_path = Path(TARGET_DIR)/'ICH/' / f'{id}.png'

        return send_file(im_path, mimetype='image/png')
    
    except (AttributeError, AssertionError) as e:
        resp = jsonify(message="No instance id provided or Data does not exist", category="error", status=404)
        return resp



@app.route('/bbox', methods=['GET','POST'])
def get_bbox():
    if flask.request.method == 'GET':
        try:
            args = request.args
            id = args.get('instance')
            original = args.get('original')
            if original is None: original = False
            json_path = Path(TARGET_DIR)/'ich' / f'{id}.json'
            edited_json_path = Path(TARGET_DIR)/'ich/' / f'{id}edit.json' #only store last edit

            if os.path.exists(edited_json_path) & (not original):
                np_path = edited_json_path
            
            return send_file(json_path, mimetype='application/json')
        
        except (AttributeError, AssertionError) as e:
            resp = jsonify(message="No instance id provided or Data does not exist", category="error", status=404)
            return resp

    else:

        annotater = Annotater(project='ich',task='box')
        try:
            update = request.get_json()
            user = request.args.get('user')
            series_id = request.args.get('series')
            annotater(user,series_id, update )
            return jsonify(success=True)
        except Exception as e:
            print(e)
            resp = jsonify(message="Only JSON is allowed. Please check on the arguments.", category="error", status=404)
            return resp

@app.route('/rot', methods=['GET'])
def rot_img():
    try:
        args = request.args
        id = args.get('instance')
        im_path = Path(TARGET_DIR)/'ich' / f'{id}_inter.png'
       
        from src.utils import rotation_calib, tilt_correction
        tilt_correction(im_path)
        send_path = str(Path(im_path).parent / Path(im_path).stem) + '_rot.png'
        return send_file(send_path, mimetype='image/png')
    
    except (AttributeError, AssertionError) as e:
        resp = jsonify(message="No instance id provided or Data does not exist", category="error", status=404)
        return resp

    
    
@app.route('/plot/<proj>/', methods=['GET'])
def plot(proj):
    try:
        args = request.args
        series = args.get('series')
        #task = args.get('task')
        
        #if not os.path.exists(Path(TARGET_DIR)/ 'tissueseg' / f'distplot_{series}.png'):
        #generate_plot(args)
        
        # check cache, gen if not in 

        if proj.lower() == 'ich':
            plot = Path(TARGET_DIR)/'ich/' / f'{instance}_bb.png' # placeholder
        elif proj.lower() in ['tissue', 'tissueseg']:
            #task = args.get('task').lower()
            #assert task in [ 'wm', 'gm', 'csf', 'vent', 'bet']
            #assert task in unet.tissue_classes , f'`task` must be one of {unet.tissue_classes}'
            plot = Path(TARGET_DIR)/ 'tissueseg' / f'distplot_{series}.png'

        return send_file(plot, mimetype='image/png')

    except (AttributeError, AssertionError) as e:
        raise e
        resp = jsonify(message=e, category="error", status=404)
        return resp

    
    
    
def perform_inference_radmix(reportText):
    try:
        # Load model
        result = findings.model(findings=reportText)
        return result
    except Exception as e:
        # Log the error for debugging purposes
        print("Error in perform_inference_radmix:", e)
        # Raise a custom exception to handle in generate_findings
        raise RuntimeError("Error occurred during inference")

@app.route('/generate_findings/', methods=['POST'])
def generate_findings():
    try:
        report = request.json['report']
        generated_report = perform_inference_radmix(report)

        return jsonify({'generated_report': generated_report})

    except (AttributeError, AssertionError) as e:
        raise e
        resp = jsonify(message=e, category="error", status=404)
        return resp


@app.route('/temp/', methods=['GET'])
def retrieve_zip():
    try:
        args = request.args
        series = args.get('series')

        # tempfix
        file_path = '/home/data_repo/cache/orthanc_copy/' + series + '.zip'

        return send_file(file_path, mimetype='application/zip')

    except (AttributeError, AssertionError) as e:
        raise e
        resp = jsonify(message=e, category="error", status=404)
        return resp


@app.route('/')
def main():
    return 'run /inference/ich/ to get json from ICH. run /inference/tissue/ to get json from tissue.'


if __name__ == '__main__':
    app.run(host='0.0.0.0')

