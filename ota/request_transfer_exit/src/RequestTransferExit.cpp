/**
 * @brief 
 * @file RequestTransferExit.cpp
 * @author Loredana Dugulean
 * @date 2024-06-26
 * 
 */

#include "RequestTransferExit.h"
#include "MCUModule.h"

/* Constructor that initializes the callback_ to nullptr */
RequestTransferExit::RequestTransferExit(int socket, Logger& RTESLogger) : callback_(nullptr), RTESLogger(RTESLogger), generate_frames(socket, RTESLogger)
{
    this->socket = socket;
}

/* Destructor */
RequestTransferExit::~RequestTransferExit()
{    
}

/* Define the service identifier for Request Transfer Exit */
const uint8_t RTES_SERVICE_ID = 0x37;

/* Method to set the callback function */
void RequestTransferExit::setTransferCompleteCallBack(transferCompleteCallBack callback)
{
    callback_ = callback;
}

/* Method to handle the request transfer exit 0x37 and invoke the callback */
bool RequestTransferExit::requestTransferExit(int id, bool transferSuccess)
{
    LOG_INFO(RTESLogger.GET_LOGGER(), "Exiting transfer with service 0x37 ");

    /* check if the callback is set */
    if (callback_)
    {
        /** Invoke the callback with the result of the transfer data
        *   returns true to continue or false to stop the transfer
        */
       bool continueTransfer = callback_(transferSuccess);

       /* Return the result from the callback indicating if the transfer should continue or stop */
       return continueTransfer;
    }

    /* If no callback is set, default to false to stop the transfer */
    return false;
}

/* Method to handle the request transfer exit 0x37 */
/* frame format = {PCI_L, SID(0x37), transfer_request_parameter_record}*/
void RequestTransferExit::requestTRansferExitRequest(canid_t can_id, const std::vector<uint8_t>& request_transfer_exit_data)
{
    NegativeResponse nrc(socket, RTESLogger);
    std::vector<uint8_t> response;
    /* Auxiliary variable used for can_id in setDidValue method */
    canid_t aux_can_id = can_id;
    /* Extract and switch sender and receiver */
    uint8_t receiver_id = can_id  & 0xFF;
    uint8_t sender_id = (can_id >> 8) & 0xFF;
    /* Reverse IDs */
    can_id = (receiver_id << 8) | sender_id;
    /* Check the frame data */
    if (request_transfer_exit_data.size() < 3)
    {
        /* Incorrect message length or invalid format - prepare a negative response */
        /* Send the negative response frame */        
        nrc.sendNRC(can_id, RTES_SERVICE_ID, NegativeResponse::IMLOIF);
        return;
    }
    else    
    {
        /* Retrieve transfer_status based on the OTA_UPDATE_STATUS_DID if it exists */
        auto value = FileManager::getDidValue(OTA_UPDATE_STATUS_DID, aux_can_id, RTESLogger)[0];
        /* Check if the transfer data has been completed */
        if (value == PROCESSING_TRANSFER_COMPLETE)        
        {
            /* prepare positive response */
            response.push_back(0x02); /* PCI */
            response.push_back(0x77); /* Service ID */
            response.push_back(request_transfer_exit_data[2]);
            /* Send the postive response frame */ 
            generate_frames.sendFrame(can_id, response);
            /* Since the response is positive, update the DID to the verification status */
            FileManager::setDidValue(OTA_UPDATE_STATUS_DID, {READY}, aux_can_id, RTESLogger, socket);
        }
        else
        {                                
            /* Request sequence error - prepare a negative response */
            /* Send the negative response frame */ 
            nrc.sendNRC(can_id, RTES_SERVICE_ID, NegativeResponse::RSE);
            /* Since the response is negative, update the DID to the verification status */
            FileManager::setDidValue(OTA_UPDATE_STATUS_DID, {IDLE}, aux_can_id, RTESLogger, socket);
            return;
        }       
    }
}
