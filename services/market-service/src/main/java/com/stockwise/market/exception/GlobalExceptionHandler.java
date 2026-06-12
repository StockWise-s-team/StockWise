package com.stockwise.market.exception;

import com.stockwise.market.adapter.in.web.dto.ErrorResponse;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

import java.time.LocalDateTime;

@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(InvalidSymbolException.class)
    public ResponseEntity<ErrorResponse> handleInvalidSymbol(InvalidSymbolException ex) {
        ErrorResponse body = new ErrorResponse("INVALID_SYMBOL", ex.getMessage(), LocalDateTime.now());
        return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(body);
    }

    @ExceptionHandler(InvalidDateRangeException.class)
    public ResponseEntity<ErrorResponse> handleInvalidDateRange(InvalidDateRangeException ex) {
        ErrorResponse body = new ErrorResponse("INVALID_DATE_RANGE", ex.getMessage(), LocalDateTime.now());
        return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(body);
    }

    @ExceptionHandler(SymbolNotFoundException.class)
    public ResponseEntity<ErrorResponse> handleSymbolNotFound(SymbolNotFoundException ex) {
        ErrorResponse body = new ErrorResponse("SYMBOL_NOT_FOUND", ex.getMessage(), LocalDateTime.now());
        return ResponseEntity.status(HttpStatus.NOT_FOUND).body(body);
    }

    @ExceptionHandler(RuntimeException.class)
    public ResponseEntity<ErrorResponse> handleRuntime(RuntimeException ex) {
        ErrorResponse body = new ErrorResponse("INTERNAL_ERROR", "An unexpected error occurred. Please try again later.", LocalDateTime.now());
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(body);
    }
}
