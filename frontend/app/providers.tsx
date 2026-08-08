"use client";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { RoleProvider } from "@/context/RoleContext";
import { useState } from "react";
export function Providers({ children }: { children: React.ReactNode }) {
const [queryClient] = useState(
() =>
new QueryClient({
defaultOptions: {
queries: {
staleTime: 60 * 1000,
refetchOnWindowFocus: false,
},
},
})
);
return (
<RoleProvider>
<QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
</RoleProvider>
);
}
