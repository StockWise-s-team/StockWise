package com.stockwise.portfolio.config;

import org.springframework.amqp.core.*;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class RabbitConfig {

    public static final String MARKET_EXCHANGE = "market.exchange";
    public static final String PORTFOLIO_PRICE_QUEUE = "portfolio_service_price_q";
    public static final String MARKET_PRICE_ROUTING_KEY = "price.updated";

    @Bean
    public TopicExchange marketExchange() {
        return new TopicExchange(MARKET_EXCHANGE);
    }

    @Bean
    public Queue portfolioPriceQueue() {
        return new Queue(PORTFOLIO_PRICE_QUEUE);
    }

    @Bean
    public Binding portfolioPriceBinding(Queue portfolioPriceQueue, TopicExchange marketExchange) {
        return BindingBuilder.bind(portfolioPriceQueue).to(marketExchange).with(MARKET_PRICE_ROUTING_KEY);
    }
}
