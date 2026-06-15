package com.stockwise.market.domain.repository;

import com.stockwise.market.domain.entity.IntradayPrice;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import java.time.Instant;
import java.util.List;

@Repository
public interface IntradayPriceRepository extends JpaRepository<IntradayPrice, Long> {

    List<IntradayPrice> findBySymbolAndTimestampAfterOrderByTimestampAsc(String symbol, Instant timestamp);

    @Modifying
    @Query("DELETE FROM IntradayPrice i WHERE i.timestamp < :timestamp")
    void deleteOlderThan(Instant timestamp);
}
