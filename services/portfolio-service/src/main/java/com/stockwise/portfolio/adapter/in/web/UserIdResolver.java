package com.stockwise.portfolio.adapter.in.web;

import com.stockwise.portfolio.application.exception.BadRequestException;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Component;

import java.util.UUID;

@Component
public class UserIdResolver {

    public UUID resolveCurrentUserId() {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication == null || !authentication.isAuthenticated() || authentication.getName() == null) {
            throw new BadRequestException("Authenticated user is required");
        }
        return UUID.fromString(authentication.getName());
    }
}
