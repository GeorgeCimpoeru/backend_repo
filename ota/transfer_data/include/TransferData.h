/**
 * @file TransferData.h
 * @author Mihnea Tanasevici
 * @brief This library represents the TransferData service.
 * It is used to transfer data to a mememory location.
 * It is using the MemoryManager class that prepares the memory in Request Download service before calling TransferData.
 */
#ifndef TRANSFER_DATA_H
#define TRANSFER_DATA_H

#include <linux/can.h>
#include "Logger.h"
#include "GenerateFrames.h"
#include "MemoryManager.h"
#include "NegativeResponse.h"
#include "RequestTransferExit.h"

#define TRANSFER_DATA_SID 0x36
class TransferData 
{
public:
/********************************************************************/
/************************* PUBLIC METHODS ***************************/
/********************************************************************/
    static constexpr uint8_t TD_SID = 0x36;
    /**
     * @brief Constructor for transfer data object
     * 
     * @param socket The socket descriptor used for communication over the CAN bus.
     * @param transfer_data_logger local reference to the parent logger
     */
    TransferData(int socket, Logger transfer_data_logger);
    /**
     * @brief method used to facilitate the transfer of data
     * 
     * @param can_id frame id that contains the sender and receiver
     * @param transfer_request data to be transferred
     */
    void transferData(canid_t can_id, std::vector<uint8_t>& transfer_request);
    /**
     * @brief Static method to get checksums for validation in transfer exit
     *    
     */
    static const std::vector<uint8_t>& getChecksums();

    /**
     * @brief Method used for processing data before it is added to the transfer data service request.
     *      This will be used only in the MCU process, right before sending the request to the ECU
     * 
     * @param can_id
     * @param current_data
     * @param socket
     * @param logger
     */
    static void processDataForTransfer(canid_t can_id, std::vector<uint8_t>& current_data, int socket, Logger& logger);
    /**
     * @brief method used to compute a simple checksum for a block of data transferred
     * 
     * @param data pointer to the data block
     * @param block_size te size of the data block
     * @return 1 byte checksum
     */
    static uint8_t computeChecksum(const uint8_t* data, size_t block_size);
/********************************************************************/
/************************* PUBLIC VARIABLES *************************/
/********************************************************************/
    static uint8_t expected_block_sequence_number;
    /* This represents 1 transfer data size, calculated in Request Download representing the  max_number_block */
    static size_t chunk_size;
    /* Used to check if all transfers are done, this is set in Request Download*/
    static MemoryManager* memory_manager;

private:
/*********************************************************************/
/************************* PRIVATE VARIABLES *************************/
/*********************************************************************/
    Logger transfer_data_logger;
    GenerateFrames generate_frames;
    int socket = -1;
    size_t total_size;
    size_t bytes_sent;
    bool memory_write_status = false;
    /* Static vector used in Request Transfer Exit thta contains the checksums for each chunk data transfer */
    static std::vector<uint8_t>checksums;
};

#endif