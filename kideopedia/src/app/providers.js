"use client"

import { CacheProvider } from "@chakra-ui/next-js"
import { ChakraProvider, createSystem, defaultConfig } from "@chakra-ui/react"

// Chakra UI v3 requires a System instance to be provided to ChakraProvider.
// Without it, ChakraProvider's context value is undefined, causing a runtime error
// like: "Cannot read properties of undefined (reading '_config')".
const system = createSystem(defaultConfig)

export default function Providers({ children }) {
  return (
    <CacheProvider>
      <ChakraProvider value={system}>{children}</ChakraProvider>
    </CacheProvider>
  )
}
