import { Navigate } from "react-router-dom";
import { ReactNode } from "react";
import { getToken } from "../services/auth";

type Props = {
  children: ReactNode;
};

export default function ProtectedRoute({ children }: Props) {
  if (!getToken()) {
    return <Navigate to="/login" replace />;
  }
  return <>{children}</>;
}
