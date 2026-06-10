package com.stockwise.market.exception;

public class SymbolNotFoundException extends RuntimeException {
    public SymbolNotFoundException(String message) {
        super(message);
    }
}
