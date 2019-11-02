#!/usr/bin/env python3

import logging
import os
import re
import subprocess
import time

IDRAC_ADDRESS_ENV  = "IDRAC_IP"
IDRAC_USERNAME_ENV = "IDRAC_USERNAME"
IDRAC_PASSWORD_ENV = "IDRAC_PASSWORD"

def get_arg_fallback_env(arg, env_fallback):
    if arg:
        return arg
    elif arg := os.environ.get(env_fallback)
        return arg
    else:
        raise EnvNotSuppliedError(env_fallback)


class EnvNotSuppliedError(Exception):
    def __init__(self, environment_variable):
        message = f"Environment variable: {environment_variable} not set."
        super().__init__(message)


class IpmiMessage:
    def __init__(self, host, username, password, cmd):
        self.__cmd = cmd.split(" ")
        self.__host = host
        self.__username = username
        self.__password = password

        self.__command = [
            "ipmitool",
            "-I",
            "lanplus",
            "-H", self.__host,
            "-U", self.__username,
            "-P", self.__password,
        ] + self.__cmd

    @property
    def out(self):
        return self.__out.decode("UTF-8")

    def send(self):
        try:
            self.__out = subprocess.check_output(self.__command)
        except subprocess.CalledProcessError as e:
            raise ValueError(
                "[IPMI] - There was an error in the IPMI message, is ipmitool installed?"
            )
        return self


class Host:
    def __init__(self, address=None):
        self.address = get_arg_fallback_env(address, IDRAC_ADDRESS_ENV)

    def to_args(self):
        return [
            "-H", self.address
        ]


class HostCredentials:
    def __init__(self, username=None, password=None):
        self.username = get_arg_fallback_env(username, IDRAC_USERNAME_ENV)
        self.password = get_arg_fallback_env(password, IDRAC_PASSWORD_ENV)

    def to_args(self):
        return [
            "-U", self.username, "-P", self.password
        ]


class Server:
    def __init__(self, host=None, username=None, password=None):
        """
        Server class for communicating with Dell R710 server.
        Credentials are provided as kwargs but fallback to env variables.
        As a last resort, username and password are the default root/calvin.

        Keyword arguments:
        host -- The IP address or hostname of the remote server
        username -- The username for ipmi remote management - default root
        password -- The password for ipmi remote management - default calvin
        """

        self.__host = host
        self.__username = username
        self.__password = password

        if self.__host == None:
            self.__host = os.environ.get("IDRAC_HOST")

        if self.__username == None:
            self.__username = os.environ.get("IDRAC_USERNAME", "root")

        if self.__password == None:
            self.__password = os.environ.get(
                "IDRAC_PASSWORD", "calvin"
            )

        if (
            self.__host == None
            or self.__username == None
            or self.__password == None
        ):
            err = f"""
            [IPMI] - Credentials were not supplied.
            Set IDRAC_HOST, IDRAC_USERNAME and IDRAC_PASSWORD as env variables, or pass them as kwargs.
            """
            raise ValueError(err)

        self.__password_redacted = "*" * len(self.__password)
        print(
            f"[IPMI] - ({self.__host}) - User: {self.__username}, Password: {self.__password_redacted}"
        )

    def do_cmd(self, cmd):
        """
        Run a ipmi command against the remote host
        Returns: the response (if any) from the server
        """
        m = IpmiMessage(
            cmd=cmd,
            host=self.__host,
            username=self.__username,
            password=self.__password,
        )
        m.send()
        return m.out

    def get_power_status(self):
        """
        Gets the power status of the server
        Returns: the power status of the server
        """
        out = self.do_cmd(cmd="power status")
        if re.search("off", out):
            power_status = "OFF"
        else:
            power_status = "ON"
        return power_status

    def power_on(self, fan_speed_pct=None):
        """
        Turns on the device. Optionally provide a fanspeed percentage to change to after boot.
        Returns: the response (if any) from the server
        """
        print(f"[IPMI] - ({self.__host}) - Powering on.")
        out = self.do_cmd(cmd="power on")
        if fan_speed_pct is not None:
            if not (fan_speed_pct >= 1 and fan_speed_pct <= 100):
                raise ValueError(
                    "The fanspeed pct should be an integer between 1-100."
                )

            time.sleep(2)
            self.set_fan_speed_manual(
                fan_speed_pct=int(fan_speed_pct)
            )
        return out

    def power_off_hard(self):
        """
        Executes a hard shutdown on the server
        Returns: the response (if any) from the server
        """
        print(f"[IPMI] - ({self.__host}) - Executing hard power off.")
        out = self.do_cmd(cmd="power off")
        return out

    def power_off_soft(self):
        """
        Executes a graceful shutdown on the server
        Returns: the response (if any) from the server
        """
        print(
            f"[IPMI] - ({self.__host}) - Executing graceful shutdown."
        )
        out = self.do_cmd(cmd="power soft")
        return out

    def power_cycle(self):
        """
        Executes a power cycle on the server (full shutdown)
        Returns: the response (if any) from the server
        """
        print(f"[IPMI] - ({self.__host}) - Executing power cycle.")
        out = self.do_cmd(cmd="power cycle")
        return out

    def power_reset(self):
        """
        Executes  warm reset on the server
        Returns: the response (if any) from the server
        """
        print(f"[IPMI] - ({self.__host}) - Executing warm reset.")
        out = self.do_cmd(cmd="power reset")
        return out

    def get_temp(self):
        """
        Gets the ambient temperature from the server
        Returns: the ambient temperature from the server
        """
        out = self.do_cmd(cmd="sdr type temperature")
        ambient_line = None
        for line in out.split("\n"):
            if "ambient" in line.lower():
                ambient_line = line

        if ambient_line is None:
            raise ValueError(
                f"[IPMI] - ({self.__host}) - Could not find ambient temp"
            )

        r = re.search("[0-9]{2}", ambient_line)
        if r:
            temp = int(r.group(0))
        else:
            temp = 0
        return temp

    def set_fan_speed_auto(self):
        """
        Sets the server fan speed to automatic.
        Returns: the response (if any) from the server
        """
        print(
            f"[IPMI] - ({self.__host}) - Returning to auto fan control."
        )
        out = self.do_cmd(cmd="raw 0x30 0x30 0x01 0x01")
        return out

    def set_fan_speed_manual(self, fan_speed_pct):
        """
        Sets the server fan speed to the percentage given in fan_speed_pct argument
        Returns: the response (if any) from the server
        """
        print(
            f"[IPMI] - ({self.__host}) - Activating manual fan control, fan speed: {fan_speed_pct}%."
        )
        out = self.do_cmd(cmd="raw 0x30 0x30 0x01 0x00")
        out = self.do_cmd(
            cmd=f"raw 0x30 0x30 0x02 0xff {hex(fan_speed_pct)}"
        )
        return out

    def get_fan_speed(self):
        """
        Gets the current fan speed from the server
        Returns: The servers current fan speed
        """
        out = self.do_cmd("sdr type fan")
        r = re.findall(r"(\d{3,})(?= RPM)", out)
        if len(r) == 0:
            r = [0]
        return int(max(r))
