import sys
from configs.data_identifiers import data_identifiers
import os
PROJECT_ROOT = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', '..', '..'))
sys.path.append(PROJECT_ROOT)
from flask import request, jsonify, Blueprint  # noqa: E402
from actions.request_id_action import RequestIdAction  # noqa: E402
from actions.update_action import Updates  # noqa: E402
from actions.routine_action import Routine  # noqa: E402
from actions.read_info_action import *  # noqa: E402
from utils.logger import log_memory  # noqa: E402
from actions.manual_send_frame import manual_send_frame  # noqa: E402
from actions.write_info_action import WriteInfo  # noqa: E402
from backend.ota.google_drive_api.GoogleDriveApi import gDrive  # noqa: E402
from actions.secure_auth import Auth  # noqa: E402
from actions.dtc_info import DiagnosticTroubleCode  # noqa: E402
from actions.diag_session import SessionManager  # noqa: E402
from actions.tester_present import Tester  # noqa: E402
from actions.access_timing_action import *  # noqa: E402
from actions.ecu_reset import Reset  # noqa: E402
from actions.security_decorator import *  # noqa: E402
from utils.input_validation import validate_update_request  # noqa: E402
from config import *  # noqa: E402
from werkzeug.exceptions import HTTPException  # noqa: E402
from actions.dtc_info import DTC_STATUS_BITS  # noqa: E402

api_bp = Blueprint('api', __name__)


@api_bp.route('/request_ids', methods=['GET'])
def request_ids():

    man_flow = request.args.get('is_manual_flow', default='true').lower() == 'false'

    if man_flow:
        session = SessionManager()
        session._change_session(2)

        auth = Auth()
        auth._auth_to()

    requester = RequestIdAction()
    response = requester.read_ids()

    return jsonify(response)


@api_bp.route('/update_to_version', methods=['POST'])
@validate_update_request
def update_to_version():
    data = request.get_json()
    sw_file_type = data.get('update_file_type')
    sw_file_version = data.get('update_file_version')
    ecu_id = data.get('ecu_id')
    address = data.get('address')
    updater = Updates()
    response = updater.update_to(type=sw_file_type,
                                 version=sw_file_version,
                                 id=ecu_id,
                                 address=address)
    return jsonify(response)


@api_bp.route('/verify_software', methods=['POST'])
def verify_software():
    data = request.get_json()
    ecu_id = data.get('ecu_id')
    routine = Routine()
    response = routine.verify_software(id=ecu_id)
    return jsonify(response)

@api_bp.route('/erase_memory', methods=['POST'])
def erase_memory():
    data = request.get_json()
    ecu_id = data.get('ecu_id')
    address = data.get('address')
    nrBytes = data.get('nrBytes')
    routine = Routine()
    response = routine.erase_memory_from_address(id=ecu_id,address=address, nrBytes=nrBytes)
    return jsonify(response)


@api_bp.route('/read_info_battery', methods=['GET'])
@requires_auth
def read_info_bat():
    reader = ReadInfo()
    item = request.args.get('item', default=None, type=str)
    response = reader.read_from_battery(item)
    return jsonify(response)


@api_bp.route('/read_info_engine', methods=['GET'])
@requires_auth
def read_info_eng():
    reader = ReadInfo()
    item = request.args.get('item', default=None, type=str)
    response = reader.read_from_engine(item)
    return jsonify(response)


@api_bp.route('/read_info_doors', methods=['GET'])
@requires_auth
def read_info_doors():
    reader = ReadInfo()
    item = request.args.get('item', default=None, type=str)
    response = reader.read_from_doors(item)
    return jsonify(response)


@api_bp.route('/read_info_hvac', methods=['GET'])
@requires_auth
def read_info_hvac():
    reader = ReadInfo()
    item = request.args.get('item', default=None, type=str)
    response = reader.read_from_hvac(item)
    return jsonify(response)


@api_bp.route('/send_frame', methods=['POST'])
def send_frame():
    data = request.get_json()
    can_id = data.get('can_id')
    can_data = data.get('can_data')
    response = manual_send_frame(can_id, can_data)
    return jsonify(response)


@api_bp.route('/write_info_doors', methods=['POST'])
@requires_auth
def write_info_doors():
    data = request.get_json()
    writer = WriteInfo(data)
    response = writer.write_to_doors(data)
    return jsonify(response)


@api_bp.route('/write_info_battery', methods=['POST'])
@requires_auth
def write_info_battery():
    data = request.get_json()
    writer = WriteInfo(data)
    response = writer.write_to_battery(data)
    return jsonify(response)


@api_bp.route('/write_info_engine', methods=['POST'])
@requires_auth
def write_info_engine():
    data = request.get_json()
    writer = WriteInfo(data)
    response = writer.write_to_engine(data)
    return jsonify(response)


@api_bp.route('/write_info_hvac', methods=['POST'])
@requires_auth
def write_info_hvac():
    data = request.get_json()
    writer = WriteInfo(data)
    response = writer.write_to_hvac(data)
    return jsonify(response)


@api_bp.route('/logs')
def get_logs():
    """ curl -X GET http://127.0.0.1:5000/api/logs """
    response = log_memory
    return jsonify({'logs': response})


@api_bp.route('/drive_update_data', methods=['GET'])
def update_drive_data():
    """ curl -X GET http://127.0.0.1:5000/api/drive_update_data """
    drive_data_json = gDrive.getDriveData()
    return jsonify(drive_data_json)


@api_bp.route('/authenticate', methods=['GET'])
def authenticate():
    try:
        auth = Auth()
        response_json = auth._auth_to()
        return jsonify(response_json), 200

    except CustomError as e:
        return jsonify(e.message), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_bp.route('/read_dtc_info', methods=['GET'])
def read_dtc_info():
    try:
        errors = []
        log_info_message(logger, f"Read DTC Info Request received: {request.args}")

        ecu_id_str = request.args.get('ecu_id', default='0x11')
        try:
            ecu_id = int(ecu_id_str, 16)
        except ValueError:
            errors.append(
                {"error": "Invalid ecu", "details": f"Ecu {ecu_id_str} is not a valid hexadecimal value"})

        requester = RequestIdAction()
        if not requester.check_ecu_up(ecu_id):
            errors.append(
                {"error": "Invalid ecu", "details": f"Ecu {hex(ecu_id)} is either not supported or not running."})

        subfunc = request.args.get('subfunc', default=1, type=int)
        if subfunc not in [1, 2]:
            errors.append({"error": "Invalid sub-function",
                          "details": f"Sub-function {subfunc} is not supported"})
        dtc_mask_bits = request.args.getlist('dtc_mask_bits')
        invalid_bits = [bit for bit in dtc_mask_bits if bit not in DTC_STATUS_BITS]

        if invalid_bits:
            errors.append({"error": "Invalid DTC mask bits",
                          "details": f"The following bits are not supported: {invalid_bits}"})

        if errors:
            return jsonify({"errors": errors})

        dtc_instance = DiagnosticTroubleCode()
        return dtc_instance.read_dtc_info(subfunc, dtc_mask_bits, ecu_id)

    except HTTPException as http_err:
        log_info_message(logger, f"HTTP Exception occurred: {http_err}")
        return jsonify({"error": "HTTP Exception occurred", "details": str(http_err)}), http_err.code
    except Exception as err:
        log_info_message(logger, f"An unexpected error occurred: {err}")
        return jsonify({"error": "An unexpected error occurred", "details": str(err)}), 500


@api_bp.route('/clear_dtc_info', methods=['POST'])
def clear_dtc_info():
    try:
        data = request.get_json()
        errors = []
        log_info_message(logger, f"Clear DTC Request received: {data}")

        ecu_id_str = data.get('ecu_id')
        try:
            ecu_id = int(ecu_id_str, 16)
        except ValueError:
            errors.append(
                {"error": "Invalid ecu", "details": f"Ecu {ecu_id_str} is not a valid hexadecimal value"})

        requester = RequestIdAction()
        if not requester.check_ecu_up(ecu_id):
            errors.append(
                {"error": "Invalid ecu", "details": f"Ecu {hex(ecu_id)} is either not supported or not running."})

        dtc_group = data.get('dtc_group')
        if errors:
            return jsonify({"errors": errors})

        clearer = DiagnosticTroubleCode()
        return clearer.clear_dtc_info(dtc_group, ecu_id)

    except CustomError as e:
        return jsonify(e.message), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_bp.route('/change_session', methods=['POST'])
def change_session():
    data = request.get_json()
    sub_funct = data.get('sub_funct')
    extra_ecu = data.get('extra_ecu')
    session = SessionManager()
    response = session._change_session(sub_funct, extra_ecu)
    return jsonify(response)


@api_bp.route('/tester_present', methods=['GET'])
def get_tester_present():
    try:
        tester = Tester()
        response = tester.is_present()
        return jsonify(response), 200

    except CustomError as e:
        return jsonify(e.message), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_bp.route('/get_identifiers', methods=['GET'])
def get_data_identifiers():
    """ curl -X GET http://127.0.0.1:5000/api/get_identifiers """
    try:
        return jsonify(data_identifiers)
    except CustomError as e:
        return jsonify(e.message), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_bp.route('/read_access_timing', methods=['POST'])
def access_timing():
    try:
        data = request.get_json()
        errors = []
        log_info_message(
            logger, f"Read Access Timing Parameters Request received: {data}")

        sub_funct = int(data.get('sub_funct'))
        if sub_funct is None:
            errors.append(
                {"status": "error", "message": "Missing 'sub_funct' parameter"})

        ecu_id_str = data.get('ecu_id')
        try:
            ecu_id = int(ecu_id_str, 16)
        except ValueError:
            errors.append(
                {"error": "Invalid ecu", "details": f"Ecu {ecu_id_str} is not a valid hexadecimal value"})

        requester = RequestIdAction()
        mcu_id = int(response_req_json.get("mcu_id"), 16)

        if not requester.check_ecu_up(ecu_id) and ecu_id != mcu_id:
            errors.append(
                {"error": "Invalid ecu", "details": f"Ecu {hex(ecu_id)} is either not supported or not running."})

        if errors:
            return jsonify({"errors": errors})

        requester = ReadAccessTiming()
        response = requester._read_timing_info(ecu_id, sub_funct)
        return jsonify(response)

    except CustomError as e:
        return jsonify(e.message), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_bp.route('/reset_ecu', methods=['POST'])
def reset_module():
    data = request.get_json()
    type_reset = data.get('type_reset')
    wh_id = data.get('ecu_id')
    reseter = Reset()
    response = reseter.reset_ecu(wh_id, type_reset)
    return jsonify(response)


@api_bp.route('/write_timing', methods=['POST'])
def write_timing():
    try:
        data = request.get_json()
        errors = []
        log_info_message(
            logger, f"Write Access Timing Parameters Request received: {data}")

        sub_funct = int(data.get('sub_funct'))
        if sub_funct is None:
            errors.append(
                {"status": "error", "message": "Missing 'sub_funct' parameter"})

        ecu_id_str = data.get('ecu_id')
        try:
            ecu_id = int(ecu_id_str, 16)
        except ValueError:
            errors.append(
                {"error": "Invalid ecu", "details": f"Ecu {ecu_id_str} is not a valid hexadecimal value"})

        requester = RequestIdAction()
        mcu_id = int(response_req_json.get("mcu_id"), 16)

        if not requester.check_ecu_up(ecu_id) and ecu_id != mcu_id:
            errors.append(
                {"error": "Invalid ecu", "details": f"Ecu {hex(ecu_id)} is either not supported or not running."})

        writer = WriteAccessTiming()
        if sub_funct == 2:
            if errors:
                return jsonify({"errors": errors})
            result = writer._write_timing_info(sub_funct, ecu_id)
        else:
            if not data or 'p2_max' not in data or 'p2_star_max' not in data:
                errors.append({"message": "Missing required parameters"})

            if errors:
                return jsonify({"errors": errors})

            p2_max = int(data.get('p2_max'))
            p2_star_max = int(data.get('p2_star_max'))

            timing_values = {
                "p2_max": p2_max,
                "p2_star_max": p2_star_max
            }
            result = writer._write_timing_info(sub_funct, ecu_id, timing_values)
        return jsonify(result)
    
    except CustomError as e:
        return jsonify(e.message), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_bp.route('ota_status', methods=['POST'])
def ota_status():
   
    data = request.get_json()
  
    # Parse the hex value from the JSON input
    ecu_id = data.get('ecu_id')
    
    if ecu_id is None:
        return jsonify({"error": "Missing hex_value"}), 400

    updater = Updates()
    response = updater.get_ota_status(ecu_id)

    return jsonify({"state": response})


@api_bp.route('/rollback_software', methods=['POST'])
def rollback_software():
    data = request.get_json()
    ecu_id = data.get('ecu_id')

    if not ecu_id:
        return jsonify({"Error": "ECU ID is required"}), 400

    try:
        updater = Updates()
        response = updater.rollback_software(ecu_id)
        return jsonify(response)

    except Exception as e:
        return jsonify({"Error": str(e)}), 500

@api_bp.route('/ota_init', methods=['POST'])
def ota_init():
    session = SessionManager()
    session._change_session(3)

    auth = Auth()
    auth._auth_to()

    data = request.get_json()
    target = data.get('target')
    version = data.get('version')

    if not target:
        return jsonify({"Error": "Target ID is required"}), 400
    if not version:
        return jsonify({"Error": "Version for software is required"}), 400

    try:
        updater = Updates()
        response = updater.ota_init(target, version)
        return jsonify(response)

    except Exception as e:
        return jsonify({"Error": str(e)}), 500

@api_bp.route('/write_to_file', methods=['POST'])
def write_to_file():
    session = SessionManager()
    session._change_session(2)

    auth = Auth()
    auth._auth_to()

    data = request.get_json()
    ecu_id = data.get('ecu_id')

    if not ecu_id:
        return jsonify({"Error": "Receiver ECU ID is required"}), 400

    try:
        updater = Updates()
        response = updater.write_to_file(ecu_id)
        return jsonify(response)

    except Exception as e:
        return jsonify({"Error": str(e)}), 500


@api_bp.route('/activate_software', methods=['POST'])
def activate_software():
    data = request.get_json()
    ecu_id = data.get('ecu_id')

    if not ecu_id:
        return jsonify({"Error": "ECU ID is required"}), 400

    try:
        updater = Updates()
        response = updater.activate_software(ecu_id)
        return jsonify(response)

    except Exception as e:
        return jsonify({"Error": str(e)}), 500

      
@api_bp.route('/sync_ota_status', methods=['POST'])
def sync_ota_status():
    data = request.get_json()
    ecu_id = data.get('ecu_id')
    ota_state = data.get('ota_state')
    updater = Updates()
    response = updater.change_ota_state(ecu_id=ecu_id, ota_status_value=ota_state)
    return jsonify(response)

  
@api_bp.route('/transfer_data_to_ecu', methods=['POST'])
def transfer_data_to_ecu():
    data = request.get_json()
    ecu_id = data.get('ecu_id')
    address = data.get('address')
    data_bytes = data.get('data_bytes')
    updater = Updates()
    response = updater.transfer_data_to_ecu(ecu_id=ecu_id, address=address, data=data_bytes)
    return jsonify(response)

@api_bp.route('/read_info', methods=['GET'])
@requires_auth
def read_info():
    item = request.args.get('item', default=None, type=str)
    
    ecu_id_str = request.args.get('ecu_id', default=None, type=str)
    try:
        ecu_id = int(ecu_id_str, 16)
    except ValueError:
        return jsonify({"error": "Invalid ecu", "details": f"Ecu {ecu_id_str} is not a valid hexadecimal value"})
    
    requester = RequestIdAction()
    if not requester.check_ecu_up(ecu_id):
        return jsonify({"error": "Invalid ecu", "details": f"Ecu {ecu_id_str} is either not supported or not running."})
    
    reader = ReadInfo()     
    response = reader.read_info(item, ecu_id)
    return jsonify(response)


@api_bp.route('/write_info', methods=['POST'])
@requires_auth
def write_info():
    data = request.get_json()

    ecu_id_str = data["ecu_id"]
    try:
        ecu_id = int(ecu_id_str, 16)
    except ValueError:
        return jsonify({"error": "Invalid ecu", "details": f"Ecu {ecu_id_str} is not a valid hexadecimal value"})
    
    requester = RequestIdAction()
    if not requester.check_ecu_up(ecu_id):
        return jsonify({"error": "Invalid ecu", "details": f"Ecu {ecu_id_str} is either not supported or not running."})
    
    writer = WriteInfo(data)
    response = writer.write_data(ecu_id, data)
    return jsonify(response)