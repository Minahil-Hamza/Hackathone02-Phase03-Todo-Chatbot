import Chat from "@/components/Chat";
import ProtectedRoute from "@/components/ProtectedRoute";

export default function Home() {
  return (
    <ProtectedRoute>
      <Chat />
    </ProtectedRoute>
  );
}
