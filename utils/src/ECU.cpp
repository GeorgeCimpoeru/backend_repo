#include "ECU.h"

std::map<uint8_t, double> ECU::timing_parameters;
std::map<uint8_t, std::future<void>> ECU::active_timers;
std::map<uint8_t, std::atomic<bool>> ECU::stop_flags;

ECU::ECU(uint8_t module_id, Logger& logger) : _module_id(module_id),
                                            _can_interface(CreateInterface::getInstance(0x00, logger)),
                                            _logger(logger)
{
    _ecu_socket = _can_interface->createSocket(ECU_INTERFACE_NUMBER);
    _frame_receiver = new ReceiveFrames(_ecu_socket, _module_id, _logger);
    sendNotificationToMCU();
}

void ECU::sendNotificationToMCU()
{
    /* Create an instance of GenerateFrames with the CAN socket */
    GenerateFrames notifyFrame = GenerateFrames(_ecu_socket, _logger);

    /* Create a vector of uint8_t (bytes) containing the data to be sent */
    std::vector<uint8_t> data = {0x01, 0xD9};

    /* Send the CAN frame with ID sender-ECU, receiver-MCU and the data vector */
    uint16_t frame_id = (_module_id << 8) | MCU_ID;
    notifyFrame.sendFrame(frame_id, data);

    LOG_INFO(_logger.GET_LOGGER(), "{:#x} sent UP notification to MCU", _module_id);
}

void ECU::startFrames()
{
    LOG_INFO(_logger.GET_LOGGER(), "{:#x} starts the frame receiver", _module_id);

    /* Create a HandleFrames object to process received frames */
    HandleFrames handleFrames(_ecu_socket, _logger);

    /* Receive a CAN frame using the frame receiver and process it with handleFrames */
    _frame_receiver->receive(handleFrames);

    /* Sleep for 100 milliseconds before receiving the next frame to prevent busy-waiting */
    std::this_thread::sleep_for(std::chrono::milliseconds(100));
}

void ECU::stopFrames()
{
    _frame_receiver->stop();
    LOG_INFO(_logger.GET_LOGGER(), "{:#x} stopped the frame receiver", _module_id);
}

ECU::~ECU()
{
    delete _frame_receiver;
    /* LOG */
}