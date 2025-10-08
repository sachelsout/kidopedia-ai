// Header.jsx
import React from "react";
import { Box, Flex, Heading, Spacer, HStack, Button } from "@chakra-ui/react";

const Header = () => {
  return (
    <Box as="header" bg="teal.500" px={6} py={4} boxShadow="sm">
      <Flex align="center">
        {/* Logo / Title */}
        <Heading as="h1" size="md" color="white">
          Kidopedia AI
        </Heading>

        <Spacer />

        {/* Navigation Links */}
        <HStack spacing={6}>
          <Button variant="link" color="white">
            Home
          </Button>
          <Button variant="link" color="white">
            About
          </Button>
          <Button variant="link" color="white">
            Contact
          </Button>
        </HStack>
      </Flex>
    </Box>
  );
};

export default Header;