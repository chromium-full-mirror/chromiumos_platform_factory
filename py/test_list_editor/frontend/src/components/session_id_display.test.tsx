// Copyright 2023 The ChromiumOS Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

import "@testing-library/jest-dom";
import { render, screen } from "@testing-library/react";
import { SessionIdFloater } from "./session_id_display";

jest.mock("../utils/user_session", () => {
  return {
    getUserSessionToken: () => ({ user_id: "12345", session_id: "54321" }),
  };
});

describe("Session Id Floater Test", () => {
  test("Renders With Expected Session Id", () => {
    render(<SessionIdFloater />);
    expect(screen.getByText(/user/i)).toBeInTheDocument();
    expect(screen.getByText(/12345/i)).toBeInTheDocument();
    expect(screen.getByText(/session/i)).toBeInTheDocument();
    expect(screen.getByText(/54321/i)).toBeInTheDocument();
  });
});
