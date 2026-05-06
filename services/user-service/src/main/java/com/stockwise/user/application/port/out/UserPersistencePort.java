package com.stockwise.user.application.port.out;

import com.stockwise.user.domain.entity.User;

import java.util.Optional;
import java.util.UUID;

public interface UserPersistencePort {
    User save(User user);
    Optional<User> findByEmail(String email);
    Optional<User> findById(UUID id);
}
