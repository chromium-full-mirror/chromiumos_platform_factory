// Copyright 2023 The ChromiumOS Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

import { getUserSessionToken } from "./user_session";

jest.mock("uuid", () => ({
  v4: () => "12345678",
}));

describe("User session Test", () => {
  beforeEach(() => {
    sessionStorage.clear();
    localStorage.clear();
  });
  test("Returns Expected Session Id.", () => {
    const { user_id, session_id } = getUserSessionToken();
    expect(user_id).toBe("12345678");
    expect(session_id).toBe("12345678");
  });
  test("Token should not be updated.", () => {
    localStorage.setItem("editor_user_token", "4321");
    sessionStorage.setItem("editor_session_token", "4321");

    const { user_id, session_id } = getUserSessionToken();

    expect(user_id).toBe("4321");
    expect(session_id).toBe("4321");
  });
});
