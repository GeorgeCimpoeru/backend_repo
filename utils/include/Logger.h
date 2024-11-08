/**
 * @file Logger.h
 * @author Iancu Daniel
 * @brief Logging module that is a wrapper for spdlog library.
 * TRACE, DEBUG, INFO, WARN, ERROR, CRITICAL logging levels available by default(customizable).
 * Logging can be turned off at compile time in the header file.
 * Logging levels accepted for logging can be changed at compile time or runtime.
 * All the logger objects share the same (static) console logger.
 * If a module wants to use a file for logging, it can create a Logger object and add a file logger to it.
 * A Logger object can have multiple file loggers, but only one static console logger (there is no need for more console loggers).
 * Log messages are flushed on each message (can be changed, depending on log level, or cyclically each ms, second etc).
 * 
 * Examples:
 *  1. Using the console logger:
 *     LOG_WARN(Logger::getConsoleLogger(), "message")
 *  2. Using the file logger:
 *      2.1. Create logger without file and add after
 *          Logger ecuLogger = Logger()
 *          ecuLogger.addFileLogger("ecuLogger", "logs/ecuLogger.txt")
 *          LOG_DEBUG(ecuLogger.getFileLogger(), "message")
 *      2.2 Create logger with file
 *          Logger ecuLogger = Logger("ecuLogger", "logs/ecuLogger.txt")
 *          LOG_DEBUG(ecuLogger.getFileLogger(), "message")
 *  3.  Disable all logs at compile time -> Logger.h -> #define SPDLOG_ACTIVE_LEVEL SPDLOG_LEVEL_OFF
 * 
 * @version 0.1
 * @date 2024-06-05
 * 
 * @copyright Copyright (c) 2024
 * 
 */

#ifndef LOGGER_H
#define LOGGER_H

#define SPDLOG_COMPILED_LIB
#define SPDLOG_ACTIVE_LEVEL SPDLOG_LEVEL_DEBUG

#define CONSOLE_LOGGER getConsoleLogger()
#define FILE_LOGGER getFileLogger()
#ifdef UNIT_TESTING_MODE
#define GET_LOGGER() CONSOLE_LOGGER
#else
#define GET_LOGGER() FILE_LOGGER
#endif /* UNIT_TESTING_MODE */
#include <spdlog/spdlog.h>
#include <spdlog/sinks/basic_file_sink.h>
#include <spdlog/sinks/stdout_color_sinks.h>

class Logger
{
private:
    /* File logger specific to a logger object. */
    std::shared_ptr<spdlog::logger> _fileLogger = nullptr;
    /* Global console logger, can be used without creating a Logger object. */
    static std::shared_ptr<spdlog::logger> _consoleLogger;
    /* Keep track of all loggers specific to a Logger object. */
    std::vector<std::string> _loggers;
public:
    /**
     * @brief Construct a new Logger object without adding a file logger to it. Only console logger by default.
     * 
     */
    Logger();

    /**
     * @brief Construct a new Logger object and add a file logger to it. The file logger is specific to this logger,
     *  but can be used in another module to log to it.
     *  
     * @param[in] loggerName Logger instance name used to categorize the log messages from different modules.
     * @param[in] filePath The path of the file where the logger will output the messages.
     */
    Logger(std::string loggerName, std::string filePath);

    /**
     * @brief Set the file logger for this Logger object.
     *  
     * @param[in] loggerName Logger instance name used to categorize the log messages from different modules.
     * @param[in] filePath The path of the file where the logger will output the messages.
     */
    void setFileLogger(std::string& loggerName, std::string& filePath);

    /**
     * @brief Create only one static consoleLogger for the Logger class. 
     * This can be used by all modules without creating a Logger object.
     * 
     * @return std::shared_ptr<spdlog::logger> 
     */
    static std::shared_ptr<spdlog::logger> getConsoleLogger();

    /**
     * @brief Retrieve the file logger associated with this Logger object.
     * 
     * @return std::shared_ptr<spdlog::logger> 
     */
    std::shared_ptr<spdlog::logger> getFileLogger() const;

    /**
     * @brief Remove a specific logger knowing its name.
     * 
     * @param[in] loggerName Logger instance name used to categorize the log messages from different modules.
     */
    void removeLogger(std::string loggerName);

    /**
     * @brief Remove all loggers specific to a Logger object.
     * Console logger is not removed.
     * 
     */
    void removeAllLoggers();

    /**
     * @brief Get the Loggers specific to this Logger (without global loggers like consoleLogger).
     * 
     * @return const std::vector<std::string>& 
     */
    const std::vector<std::string>& getLoggers() const;

    /**
     * @brief Destroy the Logger object and delete the created file loggers.
     * 
     */
    ~Logger();
};

/* LOGGING CAN BE TURNED OFF AT COMPILE TIME, BUT USAGE OF MACROS IS NEEDED IN ORDER TO WORK*/
#define LOG_TRACE(logger, ...) SPDLOG_LOGGER_TRACE(logger, __VA_ARGS__)
#define LOG_DEBUG(logger, ...) SPDLOG_LOGGER_DEBUG(logger, __VA_ARGS__)
#define LOG_INFO(logger, ...) SPDLOG_LOGGER_INFO(logger, __VA_ARGS__)
#define LOG_WARN(logger, ...) SPDLOG_LOGGER_WARN(logger, __VA_ARGS__)
#define LOG_ERROR(logger, ...) SPDLOG_LOGGER_ERROR(logger, __VA_ARGS__)
#define LOG_CRITICAL(logger, ...) SPDLOG_LOGGER_CRITICAL(logger, __VA_ARGS__)

#endif /* LOGGER_H */