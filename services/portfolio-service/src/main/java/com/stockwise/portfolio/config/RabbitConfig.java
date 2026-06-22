package com.stockwise.portfolio.config;

import org.springframework.amqp.core.*;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class RabbitConfig {

    public static final String MARKET_EXCHANGE = "market.exchange";
    public static final String PORTFOLIO_PRICE_QUEUE = "portfolio_service_price_q";
    public static final String MARKET_PRICE_ROUTING_KEY = "price.updated";

    public static final String PORTFOLIO_EXCHANGE = "portfolio.exchange";
    public static final String ORDER_EXCHANGE = "order.exchange";

    @Bean
    public TopicExchange marketExchange() {
        return new TopicExchange(MARKET_EXCHANGE);
    }

    @Bean
    public TopicExchange portfolioExchange() {
        return new TopicExchange(PORTFOLIO_EXCHANGE);
    }

    @Bean
    public TopicExchange orderExchange() {
        return new TopicExchange(ORDER_EXCHANGE);
    }

    @Bean
    public Queue portfolioPriceQueue() {
        return new Queue(PORTFOLIO_PRICE_QUEUE);
    }

    @Bean
    public Binding portfolioPriceBinding(
            @org.springframework.beans.factory.annotation.Qualifier("portfolioPriceQueue") Queue portfolioPriceQueue, 
            @org.springframework.beans.factory.annotation.Qualifier("marketExchange") TopicExchange marketExchange) {
        return BindingBuilder.bind(portfolioPriceQueue).to(marketExchange).with(MARKET_PRICE_ROUTING_KEY);
    }

    @Bean
    public org.springframework.amqp.support.converter.Jackson2JsonMessageConverter jackson2JsonMessageConverter() {
        return new org.springframework.amqp.support.converter.Jackson2JsonMessageConverter();
    }
}
