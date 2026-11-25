export const ROLE_PATHS = {
  admin: null,
  staff: ["/", "/service-types", "/services", "/catalog", "/dresses", "/customers", "/rentals", "/appointments", "/dress-lookup", "/customer-lookup", "/unreturned", "/overdue", "/reports", "/audit", "/settings"],
  cashier: ["/", "/customers", "/rentals", "/overdue", "/customer-lookup", "/reports"],
  warehouse: ["/", "/dresses", "/rentals", "/unreturned", "/overdue", "/dress-lookup"],
};

export function canAccess(role, path) {
  const allowed = ROLE_PATHS[role];
  if (!allowed) return true;
  return allowed.includes(path);
}

export function canDo(role, action) {
  const map = {
    editCatalog: ["admin", "staff"],
    collectPayment: ["admin", "staff", "cashier"],
    returnDress: ["admin", "staff", "warehouse"],
    createRental: ["admin", "staff"],
    manageUsers: ["admin"],
  };
  return (map[action] || []).includes(role);
}
