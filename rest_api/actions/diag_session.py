from actions.base_actions import *
from configs.data_identifiers import *


class SessionManager(Action):
    """ curl -X POST http://127.0.0.1:5000/api/change_session \
    -H "Content-Type: application/json" \
    -d '{
        "sub_funct": 0x03
    }'
    """
    def _change_session(self, sub_funct=1):
        """
        Changes the session control based on a given sub-function.

        Args:
        - id: The identifier of the target ECU or device.
        - sub_funct: The sub-function code to change the session.

        Returns:
        - A dictionary with the status and message of the operation.
        """

        id = (API_ID << 8) + 0x10

        try:

            session_type = "DEFAULT" if sub_funct == 1 else "PROGRAMMING" if sub_funct == 2 else "EXTENDED DIAGNOSTIC" if sub_funct == 3 else "UNKNOWN"

            if session_type == "DEFAULT":
                self.session_control(id, 0x01)
            elif session_type == "PROGRAMMING":
                self.session_control(id, 0x02)
            else:
                self.session_control(id, 0x03)

            frame_response = self._passive_response(SESSION_CONTROL, "Error changing session control")

            if frame_response.data[1] == 0x50:
                log_info_message(logger, f"Session changed to {session_type}")
                return {"message": f"Session changed to {session_type} successfully"}

            if frame_response.data[1] == 0x7F:
                negative_response = self.handle_negative_response(frame_response.data[3], frame_response.data[2])
                return {
                    "message": "Negative response received while changing session control",
                    "negative_response": negative_response
                }

        except CustomError as e:
            return {"message": f"An issue occurred while changing the session: {str(e)}. Please check the ECU status and connection."}
