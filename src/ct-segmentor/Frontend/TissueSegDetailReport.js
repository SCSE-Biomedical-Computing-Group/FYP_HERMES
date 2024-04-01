import React, { useEffect, useState, useRef } from 'react';
import { useLocation } from 'react-router-dom';
import axios from 'axios';
import { EditText, EditTextarea } from 'react-edit-text';
import 'react-edit-text/dist/index.css';
import ReportFooter from './ReportFooter';
import { FaTrashAlt } from 'react-icons/fa';
import { GiCancel } from 'react-icons/gi';

const TissueSegDetailReport = ({ props }) => {
	console.log(props);
	const [details, setDetails] = useState({});
	const [labFindingTempData, setLabFindingTemp] = useState([]);
	const [labFindingModal, setLabFindingModal] = useState(false);
	const labTitleRef = useRef();
	const labDetailRef = useRef();
	const [generatedRadmixFindings, setGeneratedRadMixFindings] = useState('');

	const mockMedicalCondition = 'No acute intracranial hemorrhage, large vascular territory infarct, edema or mass effect is present. The ventricles and sulci are normal in size and configuration. Chronic lacunar infarcts are noted in the right putamen and left subinsular white matter (446.24). There are mucus retention cysts in both maxillary sinuses as well as air-fluid levels in the frontal, ethmoidal and sphenoid sinuses, likely related to endotracheal intubation.'

	useEffect(() => {
		const fetchData = async () => {
			axios
				.get(
					`http://` + process.env.REACT_APP_BACKEND_IP_ADDRESS + process.env.REACT_APP_BACKEND_PORT_TO_RECEIVE_DATA + `/report/detail/?series=${props.series_id}&user=123456`
				)
				.then((response) => {
					const { labfindings: _, ...newObj } = response.data.content;

					setDetails(newObj);
					console.log(details);

					try {
						let temp = response.data.content.labfindings;
						for (let i = 0; i < temp.length; i++) {
							temp[i].id = i;
						}
						setLabFindingTemp(temp);
					} catch (error) {
						console.log(error);
					}

					console.log(response);
				});
		};
		fetchData();
	}, []);
	const handleSave = ({ name, value, previousValue }) => {
		alert(
			name + ' saved as: ' + value + ' (Previous Value: ' + previousValue + ')'
		);
		setDetails((prevState) => ({
			...prevState,
			[name]: value,
		}));
	};
	const handleLabSave = ({ name, value, previousValue }) => {
		alert(
			name + ' saved as: ' + value + ' (Previous Value: ' + previousValue + ')'
		);
		let temp = labFindingTempData;
		for (let i = 0; i < temp.length; i++) {
			console.log(name);
			console.log(temp[i].detail);
			if (temp[i].title === name) {
				temp[i].value = value;
			}
		}
		setLabFindingTemp(labFindingTempData);
	};

	const handleSaveAll = async () => {
		try {
			var labfindings = labFindingTempData;
			for (let i = 0; i < labfindings.length; i++) {
				console.log(labfindings[i].id);
				delete labfindings[i].id;
			}

			//converting back to object
			labfindings = { labfindings };
			const dateTimeObject = {
				date: new Date().toString(),
			};
			const series_id_obj = {
				series_id: props.series_id,
			};

			const user_id_obj = {
				user_id: 123456,
			};

			const contentObj = {
				content: { ...dateTimeObject, ...labfindings, ...details },
			};

			//Combining all objects property
			let axiosConfig = {
				headers: {
					'Content-Type': 'application/json',
				},
			};

			let postData = Object.assign(contentObj, user_id_obj, series_id_obj);
			console.log(postData);
			axios
				.post(
					`http://` + process.env.REACT_APP_BACKEND_IP_ADDRESS + process.env.REACT_APP_BACKEND_PORT_TO_RECEIVE_DATA + `/report/detail/?series=${props.series_id}&user=123456`,
					postData,
					axiosConfig
				)
				.then((response) => {
					if (response.status === 200) {
						console.log(response);
						alert('saved');
					} else {
						alert(response.statusText);
					}
				});
		} catch (error) {
			console.log(error);
		}
	};

	const handleDeleteLabFinding = (e) => {
		e.preventDefault();
		const selectedId = e.currentTarget.id;
		let temp = [];
		for (let i = 0; i < labFindingTempData.length; i++) {
			console.log(selectedId);
			console.log(labFindingTempData[i].id);
			if (labFindingTempData[i].id != selectedId) {
				temp.push(labFindingTempData[i]);
			}
		}

		for (let i = 0; i < temp.length; i++) {
			temp[i].id = i;
		}

		setLabFindingTemp(temp);
	};

	const handleAddLabFinding = () => {
		setLabFindingModal(true);
	};

	const addLabFinding = () => {
		const temp = {
			title: labTitleRef.current.value,
			value: labDetailRef.current.value,
			id: labFindingTempData.length,
		};

		setLabFindingTemp(labFindingTempData.concat([temp]));
		console.log(labFindingTempData.concat([temp]));
		setLabFindingModal(false);
		labTitleRef.current.value = '';
		labDetailRef.current.value = '';
	};

	const handleGenerateFindings = (patientDetails) => {
		console.log("Fetching generated data from server...");
		let axiosConfig = {
			headers: {
				"Content-Type": "application/json",
			},
		};
		try {
			axios
				.post(
					`http://172.21.32.4:5004/generate_findings/`,
					{
						report: patientDetails,
					},
					axiosConfig
				)
				.then((response) => {
					console.log("Data fetched successfully!");
					if (response.status === 200) {
						let generatedReport = response.data.generated_report;
						setGeneratedRadMixFindings(generatedReport);
					} else {
						console.log("Error:", response.statusText);
						alert(response.statusText);
					}
				})
				.catch((error) => {
					console.log("Error fetching data:", error);
					alert("Error fetching data");
				});
		} catch (error) {
			console.log("Error:", error);
		}
	};
	
	

	return (
		<div className='pageWrapper'>
			<div className='pageContent'>
				<div className='subContent'>
					<div className='title'>Patient Information</div>
					<div className='subContentTable'>
						<div className='grid-row-gray'>
							<div className='row-item'>Name</div>
							<div className='row-item'>ID</div>
							<div className='row-item'>DOB</div>
							<div className='row-item'>Gender</div>
						</div>
						<div className='grid-row'>
							<div className='row-item'>{props.patient_name}</div>
							<div className='row-item'>{props.patient_id}</div>
							<div className='row-item'>{props.patient_dob}</div>
							<div className='row-item'>{props.patient_gender}</div>
						</div>
					</div>
				</div>
				<div className='subContent'>
					<div className='title'>Scan Information</div>
					<div className='subContentTable'>
						<div className='grid-row-gray'>
							{/* <div className='row-item'>Acquistion DateTime</div> */}
							<div className='row-item'>Study Date</div>
							<div className='row-item'>Study Time</div>
							<div className='row-item'>Referred By</div>
							<div className='row-item'>Admitting Diagnoses</div>
						</div>
						<div className='grid-row'>
							{/* <div className='row-item'>{props.studyAcqDateTime}</div> */}
							<div className='row-item'>{props.study_date}</div>
							<div className='row-item'>{props.study_time}</div>
							<div className='row-item'>{props.patient_doctor_name}</div>
							<div className='row-item'>{props.patient_admit_desc}</div>
						</div>
					</div>
					<div className='subContentTable'>
						<div className='grid-row-gray'>
							<div className='row-item'>Modality</div>
							<div className='row-item'>Image Type</div>
							<div className='row-item'>Manufacturer</div>
							<div className='row-item'>Model Name</div>
							<div className='row-item'>Scan Options</div>
						</div>
						<div className='grid-row'>
							<div className='row-item'>{props.modality}</div>
							<div className='row-item'>{props.imageType}</div>
							<div className='row-item'>{props.manufacturer}</div>
							<div className='row-item'>{props.modelName}</div>
							<div className='row-item'>{props.scanOptions}</div>
						</div>
					</div>
				</div>
				{details.clinicalhistory && (
					<div className='subContent-nogap'>
						<div className='subTitle'>Clinical History</div>
						<EditTextarea
							className='nopaddingleft'
							defaultValue={details.clinicalhistory}
							rows={5}
							onSave={handleSave}
							name='clinicalhistory'
						/>
					</div>
				)}

				{details.imagingfindings && (
					<div className='subContent-nogap'>
						<div className='subTitle'>Imaging Findings:</div>
						<EditTextarea
							className='nopaddingleft'
							rows={5}
							defaultValue={details.imagingfindings}
							onSave={handleSave}
							name='imagingfindings'
						/>
					</div>
				)}
				{labFindingTempData && (
					<div className='subContent-nogap'>
						<div className='subTitle'>Lab Findings: </div>
						<div className='labTable'>
							<div
								className={
									labFindingModal === true ? 'lab-modal' : 'lab-modal lab-modal-hidden'
								}
							>
								<GiCancel
									className='close-modal-button'
									onClick={() => {
										setLabFindingModal(false);
									}}
									size={20}
								/>
								<div className='lab-modal-title'>Finding:</div>
								<input ref={labTitleRef}></input>
								<div className='lab-modal-title'>Results:</div>
								<input ref={labDetailRef}></input>
								<button className='btn save-button' onClick={addLabFinding}>
									Save
								</button>
							</div>
							{labFindingTempData.map((item, index) => (
								<div className='lab-row'>
									<div className='lab-row-left'>{item.title}</div>
									<div className='lab-row-right'>
										<EditText
											className='lab-finding-text-area'
											defaultValue={item.value}
											onSave={handleLabSave}
											name={item.title}
										/>
										<FaTrashAlt
											className='delete-button'
											onClick={handleDeleteLabFinding}
											size={20}
											id={item.id}
										/>
									</div>
								</div>
							))}
							<button className='add-button btn' onClick={handleAddLabFinding}>
								Add
							</button>
						</div>
					</div>
				)}
				{details.labfindingsremark && (
					<div className='subContent-nogap'>
						<div className='subTitle'>Lab Finding Remarks:</div>
						<EditTextarea
							className='nopaddingleft'
							rows={5}
							defaultValue={details.labfindingsremark}
							onSave={handleSave}
							name='imagingfindings'
						/>
					</div>
				)}
				{details.physicalexam && (
					<div className='subContent-nogap'>
						<div className='subTitle'>Physical Exam</div>
						<EditTextarea
							rows={5}
							className='nopaddingleft'
							defaultValue={details.physicalexam}
							onSave={handleSave}
							name='physicalexam'
						/>
					</div>
				)}
				<div>
					<button className="btn" onClick={handleGenerateFindings(mockMedicalCondition)}>
						Generate Findings
					</button>
				</div>
				<div className='subContent-nogap'>
						<div className='subTitle'>Generated Findings</div>
						<EditTextarea
							rows={12}
							className='nopaddingleft'
							defaultValue={generatedRadmixFindings}
							onSave={handleSave}
							name='generatedFindings'
						/>
					</div>
				<div>
					<button className='btn' onClick={handleSaveAll}>
						Save
					</button>
				</div>
				<ReportFooter />
			</div>
		</div>
	);
};

export default TissueSegDetailReport;
