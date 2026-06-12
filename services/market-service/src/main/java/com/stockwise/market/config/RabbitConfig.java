package com.stockwise.market.config;

import org.springframework.amqp.core.*;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class RabbitConfig {

    public static final String MARKET_EXCHANGE = "market.exchange";
    public static final String MARKET_PRICE_QUEUE = "market_service_price_q";
    public static final String MARKET_PRICE_ROUTING_KEY = "price.#";
    public static final String DEAD_LETTER_EXCHANGE = "market.dlx";
    public static final String DEAD_LETTER_QUEUE = "market_service_price_dlq";

    @Bean
    public TopicExchange marketExchange() {
        return new TopicExchange(MARKET_EXCHANGE, true, false);
    }

    @Bean
    public Queue marketPriceQueue() {
        return QueueBuilder
                .durable(MARKET_PRICE_QUEUE)
                .withArgument("x-dead-letter-exchange", DEAD_LETTER_EXCHANGE)
                .withArgument("x-dead-letter-routing-key", "price.dead")
                .build();
    }

    @Bean
    public Binding marketPriceBinding(Queue marketPriceQueue, TopicExchange marketExchange) {
        return BindingBuilder.bind(marketPriceQueue).to(marketExchange).with(MARKET_PRICE_ROUTING_KEY);
    }

    @Bean
    public DirectExchange deadLetterExchange() {
        return new DirectExchange(DEAD_LETTER_EXCHANGE, true, false);
    }

    @Bean
    public Queue deadLetterQueue() {
        return QueueBuilder.durable(DEAD_LETTER_QUEUE).build();
    }

    @Bean
    public Binding deadLetterBinding(Queue deadLetterQueue, DirectExchange deadLetterExchange) {
        return BindingBuilder.bind(deadLetterQueue).to(deadLetterExchange).with("price.dead");
    }
}
