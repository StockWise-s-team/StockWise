package com.stockwise.market.config;

import org.springframework.amqp.core.*;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class RabbitConfig {

    public static final String MARKET_EXCHANGE = "market.exchange";
    public static final String MARKET_PRICE_QUEUE = "market_service_price_q";
    public static final String MARKET_PRICE_ROUTING_KEY = "price.updated";

    @Bean
    public TopicExchange marketExchange() {
        return new TopicExchange(MARKET_EXCHANGE);
    }

    @Bean
    public Queue marketPriceQueue() {
        return new Queue(MARKET_PRICE_QUEUE);
    }

    @Bean
    public Binding marketPriceBinding(Queue marketPriceQueue, TopicExchange marketExchange) {
        return BindingBuilder.bind(marketPriceQueue).to(marketExchange).with(MARKET_PRICE_ROUTING_KEY);
    }
}
