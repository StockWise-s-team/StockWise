package com.stockwise.portfolio.adapter.in.web;

import com.stockwise.portfolio.adapter.in.web.dto.OrderResponse;
import com.stockwise.order.OrderConstants;
import com.stockwise.portfolio.domain.entity.Order;
import org.springframework.stereotype.Component;

@Component
public class OrderResponseMapper {

    public OrderResponse placed(Order order) {
        return new OrderResponse(order.getId(), order.getStatus(), placedMessage(order));
    }

    public OrderResponse cancelled(Order order) {
        return new OrderResponse(order.getId(), order.getStatus(), "Huy lenh thanh cong");
    }

    private String placedMessage(Order order) {
        if (OrderConstants.SELL.equals(order.getType())) {
            return "Lenh ban thanh cong, dang cho khop";
        }
        return "Lenh dat thanh cong, dang cho khop";
    }
}
