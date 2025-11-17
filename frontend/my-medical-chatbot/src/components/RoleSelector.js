import React from 'react';
import { FaUserMd, FaUser, FaUserTie, FaDollarSign } from 'react-icons/fa';

const roles = [
  { value: 'general', label: 'General / Visitor', icon: <FaUser /> },
  { value: 'doctor', label: 'Doctor / Medical Staff', icon: <FaUserMd /> },
  { value: 'receptionist', label: 'Receptionist / Front Desk', icon: <FaUserTie /> },
  { value: 'billing', label: 'Billing / Financial Services', icon: <FaDollarSign /> }
];

function RoleSelector({ userRole, setUserRole }) {
  return (
    <div className="role-selector-container">
      <label className="role-label">
        <span className="label-icon">👤</span>
        Select Your Role:
      </label>
      <div className="role-options">
        {roles.map(role => (
          <button
            key={role.value}
            className={`role-button ${userRole === role.value ? 'active' : ''}`}
            onClick={() => setUserRole(role.value)}
          >
            <span className="role-icon">{role.icon}</span>
            <span className="role-text">{role.label}</span>
          </button>
        ))}
      </div>
    </div>
  );
}

export default RoleSelector;
