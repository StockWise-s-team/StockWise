import type { OrderSide } from "@/lib/types";
import { formatQty } from "@/lib/format";

export interface OrderFormInput {
  symbol: string;
  side: OrderSide;
  quantity: string; // raw input string
  price: string; // raw input string; empty means "use default price"
  heldQuantity: number; // shares currently held for the typed symbol
}

// Pure client-side validation. Returns an error message, or null when valid.
// Server-side rules (price band, trading hours, cash sufficiency) remain
// authoritative — this only catches obvious mistakes before the request.
export function validateOrderForm(input: OrderFormInput): string | null {
  if (!input.symbol.trim()) return "Vui lòng nhập mã cổ phiếu.";

  const qty = Number(input.quantity);
  if (!Number.isInteger(qty) || qty <= 0) return "Số lượng phải là số nguyên dương.";

  if (input.price !== "") {
    const price = Number(input.price);
    if (Number.isNaN(price) || price <= 0) return "Giá đặt phải là số dương.";
  }

  if (input.side === "SELL" && input.heldQuantity < qty) {
    return `Không đủ cổ phiếu để bán (đang giữ ${formatQty(input.heldQuantity)}).`;
  }

  return null;
}
