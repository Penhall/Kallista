# tools/api/middleware_generator.py
from typing import Dict, List, Any
from pathlib import Path

class MiddlewareGenerator:
    def __init__(self):
        self.output_path = Path("output/middleware")
        self.output_path.mkdir(parents=True, exist_ok=True)

    def generate_middleware(self, middleware_config: Dict) -> str:
        """Gera código para um middleware"""
        code = []
        
        # Imports
        code.extend([
            "using System;",
            "using System.Threading.Tasks;",
            "using Microsoft.AspNetCore.Http;",
            "using Microsoft.Extensions.Logging;",
            ""
        ])

        # Classe
        code.append(f"namespace {middleware_config.get('namespace', 'YourNamespace.Middleware')}")
        code.append("{")
        code.append(f"    public class {middleware_config['name']}Middleware")
        code.append("    {")

        # Campos
        code.append("        private readonly RequestDelegate _next;")
        code.append("        private readonly ILogger _logger;")
        code.append("")

        # Construtor
        code.extend(self._generate_constructor(middleware_config))

        # Método Invoke
        code.extend(self._generate_invoke_method(middleware_config))

        code.append("    }")
        code.append("}")

        return "\n".join(code)

    def _generate_constructor(self, config: Dict) -> List[str]:
        """Gera código para o construtor do middleware"""
        code = []
        
        code.append(f"        public {config['name']}Middleware(RequestDelegate next, ILogger<{config['name']}Middleware> logger)")
        code.append("        {")
        code.append("            _next = next;")
        code.append("            _logger = logger;")
        code.append("        }")
        code.append("")
        
        return code

    def _generate_invoke_method(self, config: Dict) -> List[str]:
        """Gera código para o método Invoke do middleware"""
        code = []
        
        code.append("        public async Task InvokeAsync(HttpContext context)")
        code.append("        {")
        code.append("            try")
        code.append("            {")
        
        # Lógica específica do middleware
        if handlers := config.get('handlers', []):
            for handler in handlers:
                code.extend([f"                {line}" for line in handler['code']])
                
        code.append("                await _next(context);")
        code.append("            }")
        code.append("            catch (Exception ex)")
        code.append("            {")
        code.append('                _logger.LogError(ex, "An error occurred executing the middleware");')
        code.append("                throw;")
        code.append("            }")
        code.append("        }")
        
        return code

    def generate_exception_middleware(self) -> str:
        """Gera código para middleware de tratamento de exceções"""
        return self.generate_middleware({
            'name': 'Exception',
            'handlers': [{
                'code': [
                    "if (context.Response.HasStarted)",
                    "{",
                    "    throw new InvalidOperationException(",
                    '        "The response has already started, the exception middleware will not be executed.");',
                    "}",
                    "",
                    "try",
                    "{",
                    "    await _next(context);",
                    "}",
                    "catch (Exception ex)",
                    "{",
                    "    _logger.LogError(ex, ex.Message);",
                    "    await HandleExceptionAsync(context, ex);",
                    "}",
                ]
            }]
        })

    def generate_logging_middleware(self) -> str:
        """Gera código para middleware de logging"""
        return self.generate_middleware({
            'name': 'Logging',
            'handlers': [{
                'code': [
                    "var requestTime = DateTime.UtcNow;",
                    "",
                    '_logger.LogInformation($"Request {context.Request.Method} {context.Request.Path} started");',
                    "",
                    "await _next(context);",
                    "",
                    "var elapsed = DateTime.UtcNow - requestTime;",
                    '_logger.LogInformation($"Request {context.Request.Method} {context.Request.Path} completed in {elapsed.TotalMilliseconds}ms");'
                ]
            }]
        })

    def generate_validation_middleware(self) -> str:
        """Gera código para middleware de validação"""
        return self.generate_middleware({
            'name': 'Validation',
            'handlers': [{
                'code': [
                    "if (!context.Request.HasFormContentType)",
                    "{",
                    "    await _next(context);",
                    "    return;",
                    "}",
                    "",
                    "// Validação personalizada aqui",
                    "var validation = await ValidateRequestAsync(context);",
                    "if (!validation.IsValid)",
                    "{",
                    "    context.Response.StatusCode = StatusCodes.Status400BadRequest;",
                    "    await context.Response.WriteAsJsonAsync(validation.Errors);",
                    "    return;",
                    "}",
                    "",
                    "await _next(context);"
                ]
            }]
        })

    def save_middleware(self, name: str, code: str):
        """Salva código do middleware em arquivo"""
        file_path = self.output_path / f"{name}Middleware.cs"
        with open(file_path, 'w') as f:
            f.write(code)