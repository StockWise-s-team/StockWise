package com.stockwise.market.domain.entity;

import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

import java.math.BigDecimal;

@Entity
@Table(name = "financial_ratios")
public class FinancialRatio {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private String symbol;
    private String period;
    private BigDecimal peRatio;
    private BigDecimal pbRatio;
    private BigDecimal eps;
    private BigDecimal roe;
    private BigDecimal roa;

    public FinancialRatio() {}

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public String getSymbol() { return symbol; }
    public void setSymbol(String symbol) { this.symbol = symbol; }
    public String getPeriod() { return period; }
    public void setPeriod(String period) { this.period = period; }
    public BigDecimal getPeRatio() { return peRatio; }
    public void setPeRatio(BigDecimal peRatio) { this.peRatio = peRatio; }
    public BigDecimal getPbRatio() { return pbRatio; }
    public void setPbRatio(BigDecimal pbRatio) { this.pbRatio = pbRatio; }
    public BigDecimal getEps() { return eps; }
    public void setEps(BigDecimal eps) { this.eps = eps; }
    public BigDecimal getRoe() { return roe; }
    public void setRoe(BigDecimal roe) { this.roe = roe; }
    public BigDecimal getRoa() { return roa; }
    public void setRoa(BigDecimal roa) { this.roa = roa; }
}
